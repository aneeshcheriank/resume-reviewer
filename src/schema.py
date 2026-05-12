from pydantic import BaseModel, Field

class JDExtractorSchema(BaseModel):
    org: str = Field(description="the organization in which the postion is vaccant")
    role: str = Field(description="the organization in which the postion is vaccant")
    department: str = Field(description="the organization in which the postion is vaccant")
    hard_skills: str = Field(description="the organization in which the postion is vaccant")
    soft_skills: str = Field(description="the organization in which the postion is vaccant")
    keywords: str = Field(description="the organization in which the postion is vaccant")