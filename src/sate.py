from typing import TypedDict

class AgentState(TypedDict):
    resume: str
    jd: str
    cover_letter: str

    # jd extractor
    role: str
    department: str
    hard_skills: list[str]
    soft_skills: list[str]
    keywords: list[str]
