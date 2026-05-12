from typing import TypedDict, Annotated
import operator


class AgentState(TypedDict):
    resume: str
    jd: str
    cover_letter: str

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
    product: str
    product_and_services: str
    competition: str
