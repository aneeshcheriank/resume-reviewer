from typing import TypedDict, Annotated
import operator


class AgentState(TypedDict):

    resume: str
    job_description: str
    cover_letter: str

    # file paths for PDF editing
    resume_pdf_path: str
    cover_letter_pdf_path: str

    # jd extractor
    organization: str
    role: str
    department: str
    hard_skills: list[str]
    soft_skills: list[str]
    keywords: list[str]

    # project_research
    research_history: Annotated[list, operator.add]
    projects: list
    business_model: str
    product_and_services: str
    competition: str
    project_research_iteration: int

    # resume writer
    enhanced_resume: str
    resume_modification_explanation: str

    # cover letter writer
    enhanced_cover_letter: str
    cover_letter_modification_explanation: str
