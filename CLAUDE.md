# resume-reviewer — AI-powered resume & cover letter tailoring with PDF editing

## Overview

Upload a resume (PDF), job description (text), and optional cover letter (PDF). The app runs a LangGraph agent pipeline backed by DeepSeek that researches the company, extracts JD requirements, then rewrites both documents to maximize alignment — without fabricating experience. Changed bullet points and paragraphs are shown side-by-side with originals in the Gradio UI; you approve or reject each suggestion. Final PDFs are edited in-place with fonts, sizes, and colors preserved.

## Pipeline Graph

```
START
  → jd_extractor              extract org, role, dept, hard_skills[], soft_skills[], keywords[]
  → project_researcher         search DuckDuckGo for {org} + {dept}                  ←┐
       ↓ has tool_calls? yes → tool_call_project_research → incr iteration ──────────┘
       ↓ no (or max 5 reached)
  → project_summarizer         condense chat history into structured summary
  → project_formatter          parse summary → business_model, products, competition, important_projects[]
  → resume_writer              rewrite resume bullets using JD skills + company context
  → cover_letter_writer        enhance cover letter paragraphs (no-op if no CL provided)
  → END
```

This is a single linear pass. The only conditional branch is the DuckDuckGo research loop (capped at `max_search_calls = 5`). The old scoring loop (`resume_scorer` → `resume_writer` → loop until score ≥ 90) has been removed.

## Architecture

| Layer | Tech | File |
|-------|------|------|
| Graph framework | LangGraph `StateGraph` | `src/chain.py` |
| LLM | DeepSeek `deepseek-chat` via langchain-deepseek, temp 0.0, thinking disabled | `src/model.py` |
| Structured output | Pydantic `BaseModel` via `.with_structured_output()` | `src/schema.py` |
| State | `AgentState` TypedDict with list reducer for `research_history` | `src/state.py` |
| Tools | DuckDuckGo search (`DuckDuckGoSearchResults`, max_results=3) | `src/tools.py` |
| PDF editing | PyMuPDF (fitz) — redact spans, rewrite with original fonts/sizes/colors | `src/pdf_editor.py` |
| Change diffing | Parse into items, diff, apply user approve/reject choices | `src/diff_parser.py` |
| UI | Gradio 6.x `gr.Blocks` with `gr.File` uploads, `gr.CheckboxGroup` for approve/reject, `gr.State` for persistence | `app.py` |
| CLI | argparse — `--resume-pdf`, `--jd-file`, `--cover-letter-pdf` (optional) | `main.py` |

## File Map

```
resume-reviewer/
├── main.py                     CLI entry point
├── app.py                      Gradio UI — 3-step: upload → review & approve/reject → download
├── requirements.txt            All Python deps (pinned versions)
├── CLAUDE.md                   This file
├── README.md                   Project docs with setup & usage
│
├── src/
│   ├── agent.py                Node functions — 6 nodes + tool-call node + 1 router
│   │   ├── jd_extractor()         JD → structured output (JDExtractorSchema)
│   │   ├── project_researcher()       LLM with DuckDuckGo tool binding
│   │   ├── project_summarizer()       Summarize chat history
│   │   ├── project_formatter()        Structured output (ProjectResearcher)
│   │   ├── resume_writer()            Rewrite resume bullets (no scoring feedback)
│   │   └── cover_letter_writer()      Enhance cover letter (no-op if empty)
│   ├── chain.py               StateGraph definition — 7 nodes, linear edges, 1 conditional
│   ├── config.py              max_search_calls = 5
│   ├── diff_parser.py         parse_into_items(), diff_items(), apply_approvals()
│   ├── env.py                 dotenv.load_dotenv()
│   ├── inputs.py              get_jd(), get_resume(path), get_cover_letter(path)
│   ├── model.py               get_llm() → ChatDeepSeek instance
│   ├── pdf_editor.py          rewrite_pdf_with_new_text(original_path, new_text, output_path=None)
│   ├── prompts.py             ChatPromptTemplate definitions for all 5 pipeline prompts
│   ├── schema.py              JDExtractorSchema, ProjectResearcher, ResumeWriter, CoverLetterWriter
│   ├── state.py               AgentState TypedDict (20 fields)
│   ├── tools.py               DuckDuckGoSearchResults tool + mapping dict
│   └── utility.py             tool_call_node(history, iter_name, tool_mapping) factory
│                              router(history, map) factory
│
├── tests/
│   ├── test_schema.py         10 tests — schema validation, field_validator edge cases
│   ├── test_graph.py           8 tests — node presence, scorer removal, state key validation
│   ├── test_diff_parser.py    12 tests — parse, diff, approve/reject, change summaries
│   └── test_pdf_editor.py      7 tests — color conversion, font cache, span extraction, PDF edit/overwrite
│
└── .github/workflows/
    └── test.yml               CI — pytest on push/PR to main & claude
```

## AgentState Fields

```
resume: str                          # original resume text extracted from PDF
job_description: str                 # JD text
cover_letter: str                    # original cover letter text (empty if not provided)

resume_pdf_path: str                 # path to uploaded resume PDF (for editing)
cover_letter_pdf_path: str           # path to uploaded cover letter PDF

# jd_extractor output
organization: str
role: str
department: str
hard_skills: list[str]
soft_skills: list[str]
keywords: list[str]

# project_research (research_history uses Annotated[list, operator.add])
research_history: list              # accumulates LLM + ToolMessage objects
projects: list
business_model: str
product_and_services: str
competition: str
project_research_iteration: int

# resume_writer output
enhanced_resume: str                # rewritten resume with <modified> tags
resume_modification_explanation: str

# cover_letter_writer output
enhanced_cover_letter: str          # enhanced cover letter with <modified> tags
cover_letter_modification_explanation: str
```

## Running

```bash
# Web UI (recommended)
python app.py                         # → http://localhost:8000

# CLI
python main.py --resume-pdf inputs/Resume.pdf --jd-file inputs/jd.txt
python main.py --resume-pdf inputs/Resume.pdf --jd-file inputs/jd.txt --cover-letter-pdf inputs/cover.pdf

# Tests
pytest tests/ -v                      # 37 tests
```

### UI Workflow

1. **Upload** — three `gr.File` components for resume PDF, JD .txt, and optional cover letter PDF
2. **Generate** — click "Analyze & Generate Suggestions" → pipeline runs
3. **Review** — each changed bullet/paragraph shown as a checkbox with OLD → NEW text. Checked = approved (keep change), unchecked = rejected (revert to original)
4. **Apply & Download** — click "Apply Approved Changes & Generate PDFs" → edited PDFs appear for download

## Key Patterns & Rules

- **State updates** — Nodes return partial dicts with only the keys they modify. LangGraph merges them into the full state.
- **List accumulation** — `research_history: Annotated[list, operator.add]` causes returned `[item]` to be appended, not overwritten.
- **Tool-call loop** — `router_project_research` checks `state["research_history"][-1].tool_calls`. If present → `tool_call_project_research` which executes tools and increments `project_research_iteration`. Capped at `max_search_calls`.
- **Structured output** — `llm.with_structured_output(schema=SomeSchema)` enforces the LLM response to match the Pydantic model. The `Field(description=...)` strings guide the model.
- **Cover letter no-op** — `cover_letter_writer()` checks `if not state.get("cover_letter", "").strip()` and returns early without calling the LLM.
- **PDF editing** — `rewrite_pdf_with_new_text()`: (1) Build font cache from `page.get_fonts()` + `doc.extract_font(xref)`, (2) Extract spans via `page.get_text("dict")`, (3) Redact each span's bbox with white fill, (4) Write replacement text at original positions/original font/original size using `fitz.TextWriter`. Overwrite-safe via temp-file-then-move pattern.
- **`<modified>` tags** — The resume_writer and cover_letter_writer prompts instruct the LLM to wrap ONLY changed bullets/paragraphs in `<modified>...</modified>`. These are stripped for final output but used by `diff_parser.py` for the approval UI.
- **Approval flow** — `parse_into_items()` splits text into bullets (resume) or paragraphs (cover letter). `diff_items()` aligns by position and detects changes. `apply_approvals()` accepts a boolean list and builds the final text — approved items use the enhanced version, rejected items revert to original.
- **API key** — Set via `DEEPSEEK` environment variable, read by `src/model.py` via `os.environ.get("DEEPSEEK")`.
