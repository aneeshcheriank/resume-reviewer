import json
from pydantic import BaseModel, Field, field_validator
import re

class JDExtractorSchema(BaseModel):
    organization: str = Field(description="the organization/company in which the position is vacant")
    role: str = Field(description="the role/position title described in the job description")
    department: str = Field(description="the department the position belongs to")
    hard_skills: list[str] = Field(description="essential technical skills required for the role (e.g. Python, SQL, Docker)")
    soft_skills: list[str] = Field(description="interpersonal and complementary skills desired for the role (e.g. communication, team management)")
    keywords: list[str] = Field(description="key terms and concepts mentioned in the job description")

class ProjectResearcher(BaseModel):
    business_model: str = Field(description="Business of the organization")
    product_and_services: str = Field(description="Product and services of the organization")
    competition: str = Field(description="Compatition and competetors for the organization")
    important_projects: list[str] = Field(description="list of important projects the department is doing for the organization and why the project is important")
    # --- FIX ADDED HERE ---
    @field_validator('important_projects', mode='before')
    @classmethod
    def transform_string_to_list(cls, v):
        if isinstance(v, str):
            v = v.strip()
            # 1. Try parsing if it looks like a JSON array
            if v.startswith('[') and v.endswith(']'):
                try:
                    return json.loads(v)
                except json.JSONDecodeError:
                    pass
            
            # 2. If it's a raw paragraph, split it by sentences or bullet points so it becomes a valid list
            # This splits by periods followed by spaces, or by newlines
            project_list = [line.strip() for line in re.split(r'\. |\n', v) if line.strip()]
            if project_list:
                return project_list
                
            return [v]
        return v
    # ----------------------

class IndividualScore(BaseModel):
    hard_skills_score: int = Field(description="Resume score against hard skills")
    soft_skills_score: int = Field(description="Resume score against soft skills")
    keywords_score: int = Field(description="Resume score against keywords")

class ResumeScore(BaseModel):
    resume_score: int = Field(description="Total score of the resume agains the job description")
    detailed_score: IndividualScore = Field(description="Score optained in various categores")
    details: str = Field(description = "The resons for assining the above score")

class ResumeWriter(BaseModel):
    resume: str = Field(description="modified resume")
    explanation: str = Field(description="rationlie behiend the modification")
    

    
