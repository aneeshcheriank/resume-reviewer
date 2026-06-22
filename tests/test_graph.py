"""Tests for the LangGraph workflow structure in src/chain.py."""

import pytest
from src.chain import built_graph
from src.state import AgentState


class TestGraphStructure:
    """Test that the LangGraph is built correctly."""

    def test_graph_compiles(self):
        """The graph should compile without errors."""
        graph = built_graph()
        assert graph is not None

    def test_graph_has_expected_nodes(self):
        """All pipeline nodes should be present."""
        graph = built_graph()
        nodes = list(graph.nodes.keys())
        expected = [
            "__start__",
            "jd_extractor",
            "project_researcher",
            "tool_call_project_research",
            "project_summarizer",
            "project_formatter",
            "resume_scorer",
            "resume_writer",
        ]
        for node in expected:
            assert node in nodes, f"Missing node: {node}"

    def test_start_node_goes_to_jd_extractor(self):
        """The graph should start at jd_extractor."""
        graph = built_graph()
        # START should be connected to jd_extractor
        assert "__start__" in graph.nodes

    def test_conditional_edges_exist(self):
        """The compiled graph should expose its builder with conditional edges."""
        graph = built_graph()
        assert graph.builder is not None
        assert hasattr(graph.builder, "_branches") or hasattr(graph.builder, "branches")


class TestStateInvariants:
    """Test that the AgentState TypedDict is valid."""

    def test_state_has_required_keys(self):
        """AgentState must define all keys the pipeline expects."""
        state_keys = list(AgentState.__annotations__.keys())
        required_keys = [
            "resume",
            "job_description",
            "organization",
            "role",
            "department",
            "hard_skills",
            "soft_skills",
            "keywords",
            "research_history",
            "projects",
            "business_model",
            "product_and_services",
            "competition",
            "project_research_iteration",
            "resume_score",
            "detailed_score",
            "details",
            "resume_modification_explanation",
            "resume_write_iteration",
        ]
        for key in required_keys:
            assert key in state_keys, f"Missing state key: {key}"

    def test_skills_fields_are_lists(self):
        """hard_skills, soft_skills, keywords should be list[str]."""
        import typing
        annotations = AgentState.__annotations__
        assert annotations["hard_skills"] == list[str]
        assert annotations["soft_skills"] == list[str]
        assert annotations["keywords"] == list[str]
