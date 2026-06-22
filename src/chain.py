from langgraph.graph import StateGraph, START, END
from src.state import AgentState
from src import agent


def built_graph():
    workflow = StateGraph(AgentState)

    # nodes
    workflow.add_node("jd_extractor", agent.jd_extractor)
    workflow.add_node("project_researcher", agent.project_researcher)
    workflow.add_node("tool_call_project_research", agent.tool_call_project_research)
    workflow.add_node("project_summarizer", agent.project_summarizer)
    workflow.add_node("project_formatter", agent.project_formatter)
    workflow.add_node("resume_writer", agent.resume_writer)
    workflow.add_node("cover_letter_writer", agent.cover_letter_writer)

    # edges — single linear pass after the research loop
    workflow.add_edge(START, "jd_extractor")
    workflow.add_edge("jd_extractor", "project_researcher")
    workflow.add_edge("tool_call_project_research", "project_researcher")
    workflow.add_edge("project_summarizer", "project_formatter")
    workflow.add_edge("project_formatter", "resume_writer")
    workflow.add_edge("resume_writer", "cover_letter_writer")
    workflow.add_edge("cover_letter_writer", END)

    # conditional edges — only the research loop remains
    workflow.add_conditional_edges("project_researcher", agent.router_project_research,
                                   {
                                       "tool_call_project_research": "tool_call_project_research",
                                       "project_summarizer": "project_summarizer"
                                   })

    compiled_workflow = workflow.compile()
    return compiled_workflow
