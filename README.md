[![Test](https://github.com/aneeshcheriank/resume-reviewer/actions/workflows/test.yml/badge.svg)](https://github.com/aneeshcheriank/resume-reviewer/actions/workflows/test.yml)

# Resume Reviewer

An AI-powered resume tailoring tool that rewrites your resume to better match a target job description. Paste a job description and your resume, and the app scores your fit against the role, researches the company, then rewrites your bullet points to close the gaps — without fabricating experience.

## How It Works

The app runs a multi-step agent pipeline built with [LangGraph](https://github.com/langchain-ai/langgraph) and powered by [DeepSeek](https://deepseek.com/):

1. **JD Extraction** — parses the job description to identify the organization, role, department, hard skills, soft skills, and keywords.
2. **Company Research** — searches the web (via DuckDuckGo) to gather context about the company's business model, products, competition, and key projects.
3. **Resume Scoring** — evaluates your resume against the JD on a 0–100 scale across hard skills (50%), keywords (30%), and soft skills (20%).
4. **Resume Rewriting** — rewrites bullet points in the skills and experience sections to better align with the JD. Iterates up to 5 times until the score reaches 90. Hallucinations and keyword-stuffing are blocked by prompt guardrails.
5. **Final Output** — returns the rewritten resume, the match score, and an explanation of the changes.

## Setup

### Prerequisites

- Python 3.12+
- A [DeepSeek API key](https://platform.deepseek.com/)

### Install

```bash
git clone git@github.com:aneeshcheriank/resume-reviewer.git
cd resume-reviewer
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Configure

Set your DeepSeek API key as an environment variable:

```bash
export DEEPSEEK="sk-your-key-here"
```

### Prepare Inputs

Place your files in `inputs/`:

- `inputs/jd.txt` — the job description as plain text
- `inputs/Resume.pdf` — your resume as a PDF

## Usage

### CLI

```bash
python main.py
```

Reads from `inputs/jd.txt` and `inputs/Resume.pdf`, runs the pipeline, and prints the score and evaluation to stdout. The rewritten resume is saved to `output/resume.txt`.

### Gradio Web UI

```bash
python app.py
```

Launch a browser-based interface at `http://localhost:8000`. Paste both the job description and your resume text, then click **Generate Tailored Resume** to see the rewritten resume, match score, and modification explanation all in one place.

## Project Structure

```
resume-reviewer/
├── main.py                  # CLI entry point
├── app.py                   # Gradio web UI
├── requirements.txt         # Python dependencies
├── src/
│   ├── agent.py             # LangGraph node functions & routers
│   ├── chain.py             # Graph definition (nodes + edges)
│   ├── config.py            # Paths, iteration limits, score targets
│   ├── env.py               # dotenv loader
│   ├── inputs.py            # File readers (PDF via PyMuPDF, plain text)
│   ├── model.py             # LLM initialization (DeepSeek)
│   ├── prompts.py           # All LLM prompt templates
│   ├── schema.py            # Pydantic schemas for structured output
│   ├── state.py             # LangGraph AgentState TypedDict
│   ├── tools.py             # DuckDuckGo search tool
│   └── utility.py           # Reusable tool-call node & router factories
├── tests/
│   ├── test_schema.py       # Schema validation tests
│   └── test_graph.py        # Graph structure & state tests
├── inputs/                  # Place JD and resume here (gitignored)
├── output/                  # Generated resumes land here (gitignored)
└── .github/workflows/       # CI (runs pytest on push)
```

## Running Tests

```bash
pytest tests/ -v
```

Tests cover schema validation (including the `list[str]` field_validator for project research) and graph structure (all nodes present, state keys match the pipeline).

## License

[Apache 2.0](LICENSE)
