"""CLI entry point for the resume-reviewer pipeline.

Usage:
    python main.py --resume-pdf inputs/Resume.pdf --jd-file inputs/jd.txt
    python main.py --resume-pdf inputs/Resume.pdf --jd-file inputs/jd.txt --cover-letter-pdf inputs/cover.pdf
"""

import argparse
from pathlib import Path

from src import chain, inputs, pdf_editor


def build_initial_state(resume_text, jd_text, cover_letter_text, resume_path, cover_letter_path):
    """Build the initial state dict for the LangGraph pipeline."""
    return {
        "resume": resume_text,
        "job_description": jd_text,
        "cover_letter": cover_letter_text,

        # file paths
        "resume_pdf_path": resume_path,
        "cover_letter_pdf_path": cover_letter_path,

        # jd extractor
        "organization": "",
        "role": "",
        "department": "",
        "hard_skills": [],
        "soft_skills": [],
        "keywords": [],

        # project_research
        "research_history": [],
        "projects": [],
        "business_model": "",
        "product_and_services": "",
        "competition": "",
        "project_research_iteration": 0,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Resume Reviewer & Writer — tailor your resume to a job description"
    )
    parser.add_argument("--resume-pdf", required=True, help="Path to your resume PDF")
    parser.add_argument("--jd-file", required=True, help="Path to the job description text file")
    parser.add_argument("--cover-letter-pdf", default="", help="Path to your cover letter PDF (optional)")
    parser.add_argument("--output-resume", default="", help="Output path for edited resume (default: overwrite input)")
    parser.add_argument("--output-cover-letter", default="", help="Output path for edited cover letter (default: overwrite input)")
    args = parser.parse_args()

    # Read inputs
    print(f"Reading resume: {args.resume_pdf}")
    resume_text = inputs.get_resume(args.resume_pdf)

    print(f"Reading job description: {args.jd_file}")
    jd_text = inputs.get_jd(args.jd_file)

    cover_letter_text = ""
    if args.cover_letter_pdf:
        print(f"Reading cover letter: {args.cover_letter_pdf}")
        cover_letter_text = inputs.get_cover_letter(args.cover_letter_pdf)

    # Run pipeline
    print("Running pipeline...")
    graph = chain.built_graph()
    response = graph.invoke(build_initial_state(
        resume_text, jd_text, cover_letter_text,
        args.resume_pdf, args.cover_letter_pdf
    ))

    # Edit resume PDF in-place
    resume_out = args.output_resume or args.resume_pdf
    print(f"Editing resume PDF...")
    pdf_editor.rewrite_pdf_with_new_text(args.resume_pdf, response["enhanced_resume"], resume_out)
    print(f"Edited resume saved to: {resume_out}")
    print(f"Resume changes: {response.get('resume_modification_explanation', '')}")

    # Edit cover letter PDF in-place (if provided)
    if args.cover_letter_pdf and response.get("enhanced_cover_letter"):
        cl_out = args.output_cover_letter or args.cover_letter_pdf
        print(f"Editing cover letter PDF...")
        pdf_editor.rewrite_pdf_with_new_text(args.cover_letter_pdf, response["enhanced_cover_letter"], cl_out)
        print(f"Edited cover letter saved to: {cl_out}")
        print(f"Cover letter changes: {response.get('cover_letter_modification_explanation', '')}")

    print("Done.")
