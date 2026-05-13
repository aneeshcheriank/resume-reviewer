from src import chain
from src.inputs import get_jd

if __name__== "__main__":
    jd = get_jd()
    build_cahin = chain.built_graph()
    response = build_cahin.invoke({
        "query": "start the process",

        "resume": "",
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
        "project_research_iteration": 0
    })

    keys  = [
        "organization",
        "role",
        "department",
        "hard_skills",
        "soft_skills",
        "keywords",
    
        # project_research
        "projects",
        "business_model",
        "product_and_services",
        "competition"
    ]
    for key in keys:
        print(f"{key}: {response.get(key)}")
        print("\n")

    