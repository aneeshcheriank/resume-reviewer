import gradio as gr

from src import chain

# 1. FIXED TYPO HERE (rewrtie -> rewrite)
def rewrite_resume(jd, resume):

    build_chain = chain.built_graph()
    response = build_chain.invoke({
        "resume": resume,
        "job_description": jd,
        "cover_letter": "",
    
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

        # resume score
        "resume_score": 0,  
        "detailed_score": {},
        "details": "",

        # resume writer
        "resume_write_iteration": 0
    })

    return (
        response.get("resume", ""),
        str(response.get("resume_score", "")),
        response.get("resume_modification_explanation", "")
    )


with gr.Blocks() as app:
    gr.Markdown("# Resume Reviewer & Writer")
    
    # Left side: Input, Right side: Output Resume
    with gr.Row():
        with gr.Column():
            gr.Markdown("### 1. Paste Job Description")
            job_description = gr.Textbox(lines=20, placeholder="Paste the job description here...", show_label=False)

        with gr.Column():
            gr.Markdown("### 2. paste Resume")
            resume = gr.Textbox(lines=20, placeholder="Paste the job description here...", show_label=False)
    with gr.Row():
        button = gr.Button("Generate Tailored Resume", variant="primary") # variant="primary" makes it a prominent button

    with gr.Row():
        with gr.Column():
            gr.Markdown("### 2. Rewritten Resume")
            rewritten_resume = gr.Textbox(lines=20, label="Rewritten resume")
        with gr.Column():
            gr.Markdown("### Feedback")
            exp = gr.Textbox(label="Modification Explanation", lines=5)

    # Bottom section for evaluation metrics
    gr.Markdown("---")
    gr.Markdown("### 3. Evaluation")
    with gr.Row():
        score = gr.Textbox(label="Match Score", scale=1) # scale makes it smaller
        

    # 2. FIXED CALL HERE (Matches the fixed function name)
    button.click(
        fn=rewrite_resume,
        inputs=[job_description, resume],
        outputs=[rewritten_resume, score, exp]
    )

app.launch(server_name="0.0.0.0", server_port=8000, debug=True)