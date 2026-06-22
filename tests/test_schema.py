"""Tests for Pydantic schemas in src/schema.py."""

import pytest
from src.schema import JDExtractorSchema, ProjectResearcher, ResumeScore, ResumeWriter


class TestJDExtractorSchema:
    """Test the JD Extractor schema validates correctly."""

    def test_valid_input(self):
        data = {
            "organization": "Acme Corp",
            "role": "Machine Learning Engineer",
            "department": "Data Engineering",
            "hard_skills": ["Python", "PyTorch", "SQL"],
            "soft_skills": ["Communication", "Team Management"],
            "keywords": ["deep learning", "NLP", "ETL"],
        }
        result = JDExtractorSchema(**data)
        assert result.organization == "Acme Corp"
        assert result.hard_skills == ["Python", "PyTorch", "SQL"]

    def test_fields_are_correct_types(self):
        result = JDExtractorSchema(
            organization="TestOrg",
            role="Dev",
            department="Eng",
            hard_skills=["skill1"],
            soft_skills=["skill2"],
            keywords=["kw1"],
        )
        assert isinstance(result.hard_skills, list)
        assert isinstance(result.soft_skills, list)
        assert isinstance(result.keywords, list)


class TestProjectResearcher:
    """Test the Project Researcher schema, including the field_validator."""

    def test_valid_list_input(self):
        data = {
            "business_model": "SaaS",
            "product_and_services": "Cloud platform",
            "competition": "AWS, Azure",
            "important_projects": ["Migration to microservices", "AI chatbot"],
        }
        result = ProjectResearcher(**data)
        assert len(result.important_projects) == 2
        assert result.important_projects[0] == "Migration to microservices"

    def test_string_converted_to_list(self):
        """field_validator should convert a comma-separated string to a list."""
        data = {
            "business_model": "SaaS",
            "product_and_services": "Cloud",
            "competition": "Competitors",
            "important_projects": "Migration project. AI initiative",
        }
        result = ProjectResearcher(**data)
        assert isinstance(result.important_projects, list)
        assert len(result.important_projects) > 0

    def test_json_array_string_converted(self):
        """field_validator should parse a JSON array string."""
        data = {
            "business_model": "SaaS",
            "product_and_services": "Cloud",
            "competition": "Competitors",
            "important_projects": '["Project Alpha", "Project Beta"]',
        }
        result = ProjectResearcher(**data)
        assert result.important_projects == ["Project Alpha", "Project Beta"]

    def test_single_string_wrapped_in_list(self):
        """A plain string should be wrapped into a single-element list."""
        data = {
            "business_model": "SaaS",
            "product_and_services": "Cloud",
            "competition": "Competitors",
            "important_projects": "Only one project",
        }
        result = ProjectResearcher(**data)
        assert result.important_projects == ["Only one project"]


class TestResumeScore:
    """Test the Resume Score schema."""

    def test_valid_score(self):
        data = {
            "resume_score": 85,
            "detailed_score": {
                "hard_skills_score": 40,
                "soft_skills_score": 18,
                "keywords_score": 27,
            },
            "details": "Good match, missing some keywords.",
        }
        result = ResumeScore(**data)
        assert result.resume_score == 85
        assert result.detailed_score.hard_skills_score == 40


class TestResumeWriter:
    """Test the Resume Writer schema."""

    def test_valid_output(self):
        data = {
            "resume": "Rewritten resume content here...",
            "explanation": "Improved bullet points for clarity.",
        }
        result = ResumeWriter(**data)
        assert "Rewritten" in result.resume
        assert result.explanation == "Improved bullet points for clarity."
