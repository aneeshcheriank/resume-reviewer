from pydantic import BaseModel, Field

class JDExtractorSchema(BaseModel):
    org: str = Field(description="the organization in which the postion is vaccant")
    role: str = Field(description="the organization in which the postion is vaccant")
    department: str = Field(description="the organization in which the postion is vaccant")
    hard_skills: str = Field(description="the organization in which the postion is vaccant")
    soft_skills: str = Field(description="the organization in which the postion is vaccant")
    keywords: str = Field(description="the organization in which the postion is vaccant")

class ProjectResearcher(BaseModel):
    business_model: str = Field(description="Business of the organization")
    product_and_services: str = Field(description="Product and services of the organization")
    competition: str = Field(description="Compatition and competetors for the organization")
    important_projects: list[str] = Field(description="list of important projects the department is doing for the organization and why the project is important")
