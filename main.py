from pathlib import Path

from src import chain
from src.inputs import get_jd, get_resume
from src.config import resume_path, jd_path

output_path = "output/resume.txt"

if __name__== "__main__":
    jd = get_jd(jd_path)
    resume = get_resume(resume_path)
    build_cahin = chain.built_graph()
    response = build_cahin.invoke({

        "resume": resume,
        "job_description": jd,
        "cover_letter": "",
    
        # jd extractor
        "organization": "",
        "role": "",
        "department": "",
        "hard_skills": "",
        "soft_skills": "",
        "keywords": "",
    
        # project_research
        "research_history": [],
        "projects": [],
        "business_model": "",
        "product": "",
        "product_and_services": "",
        "competition": "",
        "project_research_iteration": 0,

        # resume writer
        "resume_write_iteration": 0
    })

    file_path = Path(output_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, "w") as f:
        f.write(response.get("resume", ""))


    keys  = [
        # "organization",
        # "role",
        # "department",
        # "hard_skills",
        # "soft_skills",
        # "keywords",
    
        # # project_research
        # "projects",
        # "business_model",
        # "product_and_services",
        # "competition",

        # resume score
        "resume_score",
        "detailed_score",
        "details"
    ]
    for key in keys:
        print(f"{key}: {response.get(key)}")
        print("\n")

    