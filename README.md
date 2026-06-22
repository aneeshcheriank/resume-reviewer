[![Test](https://github.com/aneeshcheriank/resume-reviewer/actions/workflows/test.yml/badge.svg)](https://github.com/aneeshcheriank/resume-reviewer/actions/workflows/test.yml)

# Resume Reviewer

An AI-powered resume and cover letter tailoring tool. Upload your PDFs, paste a job description, and the app researches the company, extracts JD requirements, then rewrites both documents to maximize alignment — **directly editing the PDFs while preserving fonts and formatting**. A Gradio UI lets you review each suggested change and approve or reject it before downloading the final files.

## How It Works

A LangGraph agent pipeline backed by DeepSeek runs five steps:

1. **JD Extraction** — parses the job description into organization, role, department, hard skills, soft skills, and keywords.
2. **Company Research** — searches the web (DuckDuckGo) for the company's business model, products, competition, and key projects.
3. **Resume Rewriting** — rewrites bullet points in the skills and experience sections to align with the JD and company domain, without fabricating experience.
4. **Cover Letter Enhancement** — tailors the cover letter narrative using JD insights and company research (skipped if no cover letter is uploaded).
5. **Review & Approve** — each changed bullet or paragraph is shown as a toggle: old text vs. new text. Check to keep, uncheck to reject.
6. **PDF Editing** — final PDFs are written with the original fonts, sizes, and colors preserved using PyMuPDF.

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

```bash
export DEEPSEEK="sk-your-key-here"
```

## Usage

### Web UI

```bash
python app.py
```

Opens at `http://localhost:8000`. Three steps:

1. **Upload** — select resume PDF, job description (.txt), and optional cover letter PDF
2. **Review** — each suggested change shown as a checkbox with old → new text. Uncheck anything you want to reject
3. **Download** — click "Apply Approved Changes & Generate PDFs" to get your edited files

### CLI

```bash
# Resume only
python main.py --resume-pdf inputs/Resume.pdf --jd-file inputs/jd.txt

# Resume + cover letter
python main.py --resume-pdf inputs/Resume.pdf --jd-file inputs/jd.txt --cover-letter-pdf inputs/cover.pdf
```

Edited PDFs are saved in-place (overwriting the originals — make backups first).

## Project Structure

```
resume-reviewer/
├── main.py                     CLI entry point
├── app.py                      Gradio web UI
├── requirements.txt            Python dependencies
├── src/
│   ├── agent.py                LangGraph node functions (6 nodes + tool-call + router)
│   ├── chain.py                StateGraph definition
│   ├── config.py               max_search_calls = 5
│   ├── diff_parser.py          Parse, diff, and approve/reject text changes
│   ├── env.py                  dotenv loader
│   ├── inputs.py               File readers (PDF via PyMuPDF, plain text)
│   ├── model.py                LLM init (DeepSeek deepseek-chat, temp 0.0)
│   ├── pdf_editor.py           Format-preserving PDF text replacement
│   ├── prompts.py              LLM prompt templates (5 prompts)
│   ├── schema.py               Pydantic schemas (4 schemas)
│   ├── state.py                AgentState TypedDict
│   ├── tools.py                DuckDuckGo search tool
│   └── utility.py              tool_call_node() and router() factories
├── tests/
│   ├── test_schema.py          Schema validation (10 tests)
│   ├── test_graph.py           Graph structure & state (8 tests)
│   ├── test_diff_parser.py     Diff parsing & approval logic (12 tests)
│   └── test_pdf_editor.py      PDF editing functions (7 tests)
├── inputs/                     Input files (gitignored)
├── output/                     Generated files (gitignored)
└── .github/workflows/          CI — pytest on push
```

## Running Tests

```bash
pytest tests/ -v
```

**37 tests** covering schemas, graph structure, diff parsing, approval logic, and PDF editing.

## License

[Apache 2.0](LICENSE)
