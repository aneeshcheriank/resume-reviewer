"""Gradio web UI for the resume-reviewer pipeline.

Three-step workflow:
1. Upload resume PDF, job description file, and optional cover letter PDF
2. Review the AI-suggested changes — approve or reject each one individually
3. Download the edited PDFs with only approved changes applied
"""

import tempfile
import os
from pathlib import Path

import gradio as gr

from src import chain, inputs, pdf_editor, diff_parser


def build_initial_state(resume_text, jd_text, cover_letter_text, resume_path, cover_letter_path):
    """Build the initial state dict for the LangGraph pipeline."""
    return {
        "resume": resume_text,
        "job_description": jd_text,
        "cover_letter": cover_letter_text,

        "resume_pdf_path": resume_path,
        "cover_letter_pdf_path": cover_letter_path,

        "organization": "",
        "role": "",
        "department": "",
        "hard_skills": [],
        "soft_skills": [],
        "keywords": [],

        "research_history": [],
        "projects": [],
        "business_model": "",
        "product_and_services": "",
        "competition": "",
        "project_research_iteration": 0,
    }


def _make_checkbox_label(index, old_text, new_text):
    """Create a readable label for a change checkbox."""
    old_short = old_text[:120] + "..." if len(old_text) > 120 else old_text
    new_short = new_text[:120] + "..." if len(new_text) > 120 else new_text
    return f"[{index+1}] OLD: {old_short}  →  NEW: {new_short}"


def process_files(resume_pdf, jd_file, cover_letter_pdf):
    """Step 1: Read uploaded files, run the pipeline, return change data."""
    if resume_pdf is None:
        return (
            [], [], [], "", "",
            gr.update(choices=[], value=[]),
            gr.update(choices=[], value=[]),
            "", "", "", "", "", "", "", "",
            "⚠️ Please upload a resume PDF.",
        )
    if jd_file is None:
        return (
            [], [], [], "", "",
            gr.update(choices=[], value=[]),
            gr.update(choices=[], value=[]),
            "", "", "", "", "", "", "", "",
            "⚠️ Please upload a job description file.",
        )

    # Read resume
    resume_path = resume_pdf if isinstance(resume_pdf, str) else resume_pdf.name
    resume_text = inputs.get_resume(resume_path)

    # Read JD
    if isinstance(jd_file, str):
        jd_text = Path(jd_file).read_text()
    else:
        jd_text = jd_file.decode("utf-8") if isinstance(jd_file, bytes) else Path(jd_file.name).read_text()

    # Read optional cover letter
    cover_letter_text = ""
    cover_letter_path = ""
    if cover_letter_pdf is not None:
        cover_letter_path = cover_letter_pdf if isinstance(cover_letter_pdf, str) else cover_letter_pdf.name
        cover_letter_text = inputs.get_cover_letter(cover_letter_path)

    # Run pipeline
    graph = chain.built_graph()
    response = graph.invoke(build_initial_state(
        resume_text, jd_text, cover_letter_text,
        resume_path, cover_letter_path
    ))

    enhanced_resume = response.get("enhanced_resume", "")
    enhanced_cover_letter = response.get("enhanced_cover_letter", "")
    resume_explanation = response.get("resume_modification_explanation", "")
    cover_explanation = response.get("cover_letter_modification_explanation", "")

    # Parse changes
    resume_orig_items, resume_enhanced_items, resume_diffs = diff_parser.extract_change_summary(
        resume_text, enhanced_resume, mode="bullets"
    )
    cl_orig_items, cl_enhanced_items, cl_diffs = ([], [], [])
    if cover_letter_text:
        cl_orig_items, cl_enhanced_items, cl_diffs = diff_parser.extract_change_summary(
            cover_letter_text, enhanced_cover_letter, mode="paragraphs"
        )

    # Build checkbox choices — only show changed items
    resume_changed = [d for d in resume_diffs if d["changed"]]
    if resume_changed:
        resume_checkbox_choices = [
            _make_checkbox_label(d["index"], d["old_text"], d["new_text"])
            for d in resume_changed
        ]
        # Default: all approved
        resume_checkbox_default = resume_checkbox_choices[:]
    else:
        resume_checkbox_choices = ["(No changes to resume bullet points)"]
        resume_checkbox_default = []

    cl_changed = [d for d in cl_diffs if d["changed"]]
    if cl_changed:
        cl_checkbox_choices = [
            _make_checkbox_label(d["index"], d["old_text"], d["new_text"])
            for d in cl_changed
        ]
        cl_checkbox_default = cl_checkbox_choices[:]
    else:
        cl_checkbox_choices = ["(No changes to cover letter paragraphs)"]
        cl_checkbox_default = []

    # Build preview text with all changes applied
    preview = diff_parser.apply_approvals(resume_orig_items, resume_enhanced_items,
                                          [True] * len(resume_enhanced_items))

    return (
        resume_orig_items, resume_enhanced_items, resume_path,
        cl_orig_items, cl_enhanced_items, cl_path,
        gr.update(choices=resume_checkbox_choices, value=resume_checkbox_default),
        gr.update(choices=cl_checkbox_choices, value=cl_checkbox_default),
        enhanced_resume, enhanced_cover_letter,
        resume_explanation, cover_explanation,
        preview, "",
        "",  # clear status message
    )


def apply_and_generate(resume_orig_items, resume_enhanced_items, resume_path,
                       cl_orig_items, cl_enhanced_items, cl_path,
                       resume_approved_labels, cl_approved_labels):
    """Step 2: Apply user's approve/reject choices and generate PDFs."""
    if not resume_path:
        return None, None, "⚠️ Upload files first."

    resume_out_path = None
    cl_out_path = None

    # Determine which resume items were approved
    if resume_orig_items and resume_enhanced_items:
        # The approved_labels are the checkbox labels that were selected
        # Parse out the index from each approved label
        approved_indices = set()
        for label in resume_approved_labels:
            # Label format: "[N] OLD: ...  →  NEW: ..."
            # Extract N
            try:
                idx_str = label.split("]")[0].lstrip("[")
                approved_indices.add(int(idx_str) - 1)
            except (ValueError, IndexError):
                continue

        # Build approvals list
        resume_approvals = []
        for i in range(len(resume_enhanced_items)):
            resume_approvals.append(i in approved_indices)

        final_resume = diff_parser.apply_approvals(
            resume_orig_items, resume_enhanced_items, resume_approvals
        )
        resume_out = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
        resume_out.close()
        pdf_editor.rewrite_pdf_with_new_text(resume_path, final_resume, resume_out.name)
        resume_out_path = resume_out.name

    # Same for cover letter
    if cl_path and cl_orig_items and cl_enhanced_items:
        approved_indices = set()
        for label in cl_approved_labels:
            try:
                idx_str = label.split("]")[0].lstrip("[")
                approved_indices.add(int(idx_str) - 1)
            except (ValueError, IndexError):
                continue

        cl_approvals = []
        for i in range(len(cl_enhanced_items)):
            cl_approvals.append(i in approved_indices)

        final_cl = diff_parser.apply_approvals(
            cl_orig_items, cl_enhanced_items, cl_approvals
        )
        cl_out = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
        cl_out.close()
        pdf_editor.rewrite_pdf_with_new_text(cl_path, final_cl, cl_out.name)
        cl_out_path = cl_out.name

    return resume_out_path, cl_out_path, "✅ PDFs generated! Download them below."


# ── Gradio UI ──────────────────────────────────────────────────────────────────

with gr.Blocks(title="Resume Reviewer & Writer") as app:
    gr.Markdown("# 📄 Resume Reviewer & Writer")
    gr.Markdown("Upload your resume, a job description, and optionally a cover letter. "
                "The AI suggests changes — **approve or reject each one** — then download edited PDFs.")

    # Hidden state
    state_resume_orig = gr.State([])
    state_resume_enhanced = gr.State([])
    state_resume_path = gr.State("")
    state_cl_orig = gr.State([])
    state_cl_enhanced = gr.State([])
    state_cl_path = gr.State("")

    # ═══════════════ STEP 1: Upload ═══════════════
    gr.Markdown("## Step 1: Upload Files")

    with gr.Row():
        with gr.Column():
            gr.Markdown("### Resume 📋")
            resume_input = gr.File(
                file_types=[".pdf"], file_count="single",
                label="Upload Resume (PDF)",
            )
        with gr.Column():
            gr.Markdown("### Job Description 📝")
            jd_input = gr.File(
                file_types=[".txt"], file_count="single",
                label="Upload Job Description (.txt)",
            )
        with gr.Column():
            gr.Markdown("### Cover Letter ✉️ (optional)")
            cover_letter_input = gr.File(
                file_types=[".pdf"], file_count="single",
                label="Upload Cover Letter (PDF)",
            )

    generate_btn = gr.Button("🔍 Analyze & Generate Suggestions", variant="primary", size="lg")
    status_msg = gr.Markdown("")

    # ═══════════════ STEP 2: Review & Approve ═══════════════
    gr.Markdown("---")
    gr.Markdown("## Step 2: Review & Approve Changes")
    gr.Markdown("Each checkbox is a suggested change. **Checked = Approved (keep)**. Uncheck to reject and revert to original.")

    with gr.Row():
        with gr.Column():
            gr.Markdown("### Resume Changes")
            resume_checkboxes = gr.CheckboxGroup(
                label="Approve resume changes",
                choices=[],
                value=[],
                interactive=True,
            )
        with gr.Column():
            gr.Markdown("### Cover Letter Changes")
            cover_letter_checkboxes = gr.CheckboxGroup(
                label="Approve cover letter changes",
                choices=[],
                value=[],
                interactive=True,
            )

    gr.Markdown("### Change Explanations")
    with gr.Row():
        resume_explanation = gr.Textbox(label="Resume Modification Rationale", lines=3, interactive=False)
        cover_letter_explanation = gr.Textbox(label="Cover Letter Modification Rationale", lines=3, interactive=False)

    with gr.Accordion("📝 Live Preview of Final Resume (all approved changes applied)", open=False):
        preview_text = gr.Textbox(label="Final Resume", lines=15, interactive=False)

    apply_btn = gr.Button("✅ Apply Approved Changes & Generate PDFs", variant="primary", size="lg")

    # ═══════════════ STEP 3: Download ═══════════════
    gr.Markdown("---")
    gr.Markdown("## Step 3: Download Edited PDFs")

    with gr.Row():
        with gr.Column():
            resume_download = gr.File(label="📥 Download Edited Resume", visible=True)
        with gr.Column():
            cover_letter_download = gr.File(label="📥 Download Edited Cover Letter", visible=True)

    # ═══════════════ Event Handlers ═══════════════

    generate_btn.click(
        fn=process_files,
        inputs=[resume_input, jd_input, cover_letter_input],
        outputs=[
            state_resume_orig, state_resume_enhanced, state_resume_path,
            state_cl_orig, state_cl_enhanced, state_cl_path,
            resume_checkboxes, cover_letter_checkboxes,
            preview_text, gr.State(),  # not used for raw enhanced texts
            resume_explanation, cover_letter_explanation,
            preview_text, gr.State(),
            status_msg,
        ],
    )

    apply_btn.click(
        fn=apply_and_generate,
        inputs=[
            state_resume_orig, state_resume_enhanced, state_resume_path,
            state_cl_orig, state_cl_enhanced, state_cl_path,
            resume_checkboxes, cover_letter_checkboxes,
        ],
        outputs=[resume_download, cover_letter_download, status_msg],
    )

app.launch(server_name="0.0.0.0", server_port=8000, debug=True)
