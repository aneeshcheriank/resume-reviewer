# resume-reviewer — AI-powered resume tailoring

## Overview

This app takes a job description and resume as input, runs a LangGraph agent pipeline backed by DeepSeek, and rewrites the resume to better match the JD. It scores fit, researches the company via DuckDuckGo, and iterates until the score hits a threshold. Two entry points: CLI (`main.py`) and Gradio web UI (`app.py`).

## Pipeline Graph

```
START
  → jd_extractor               parse JD → org, role, dept, hard_skills[], soft_skills[], keywords[]
  → project_researcher          search DuckDuckGo for {org} + {dept}    ←┐
       ↓ tool_calls? yes → tool_call_project_research → incr counter ────┘  (max 5 searches)
       ↓ no
  → project_summarizer          condense research chat into summary
  → project_formatter           structured output: business_model, products, competition, projects[]
  → resume_scorer               score 0-100 (50% hard skills / 30% keywords / 20% soft skills)
       ↓ score < 90 & iter < 5 → resume_writer → rewrite bullet points → loops back to scorer
       ↓ score ≥ 90 or iter ≥ 5
  → END
```

## Architecture

- **Framework**: [LangGraph](https://github.com/langchain-ai/langgraph) (`src/chain.py` builds the `StateGraph`)
- **LLM**: DeepSeek via `langchain-deepseek` (`src/model.py`)
- **Structured output**: Pydantic schemas (`src/schema.py`) enforce output format via `.with_structured_output()`
- **Tools**: DuckDuckGo search (`src/tools.py`) for company research, with tool-call loop
- **State**: Single `AgentState` TypedDict flows through all nodes (`src/state.py`)

## Key Files

| File | Role |
|---|---|
| `main.py` | CLI — reads `inputs/jd.txt` + `inputs/Resume.pdf`, invokes graph, writes `output/resume.txt` |
| `app.py` | Gradio UI — paste JD + resume text, see rewritten resume + score + explanation |
| `src/chain.py` | Graph definition: nodes, edges, conditional edges |
| `src/agent.py` | Node functions (jd_extractor, project_researcher, summarizer, formatter, scorer, writer) + routers |
| `src/prompts.py` | All ChatPromptTemplate definitions |
| `src/schema.py` | Pydantic models: JDExtractorSchema, ProjectResearcher, ResumeScore, ResumeWriter |
| `src/state.py` | `AgentState` TypedDict with all flow variables |
| `src/tools.py` | DuckDuckGo search tool + tool mapping |
| `src/utility.py` | Reusable `tool_call_node` and `router` factories |
| `src/config.py` | Paths, `max_search_calls=5`, `resume_matching_score=90`, `max_resume_write_iteration=5` |
| `src/inputs.py` | PDF reader (PyMuPDF) + plain text reader |

## Running

```bash
# CLI
python main.py

# Web UI (localhost:8000)
python app.py

# Tests
pytest tests/ -v
```

## Important Rules When Editing

- **`AgentState` keys** (`src/state.py`) must match exactly what nodes return — the graph merges partial state updates by key name.
- **Lists that accumulate** (e.g. `research_history`) use `Annotated[list, operator.add]` in state; nodes return `[new_item]` and LangGraph appends.
- **Router return values** are node names or `END`. A router that returns `END` is how the resume-scorer loop terminates.
- **`.with_structured_output(schema=...)`** requires the schema to extend `BaseModel` and have proper `Field(description=...)` — the descriptions guide the LLM.
- **`config.max_search_calls`** caps the tool-call loop in `project_researcher` to prevent infinite DuckDuckGo searches.
- **Resume writer guardrails** in the prompt (`src/prompts.py`): no hallucinations, no keyword-stuffing, no domain cross-pollination, `<modified>` tags around changed bullets.
- Tests are run via `pytest tests/ -v` — 14 tests covering schema validators and graph structure. CI runs on push/PR to `main` and `claude`.
