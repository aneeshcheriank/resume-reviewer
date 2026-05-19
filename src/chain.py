from langgraph.graph import StateGraph, START, END
from src.state import AgentState
from src import agent

def built_graph():
    workflow = StateGraph(AgentState)

    #nodes
    workflow.add_node("jd_extractor", agent.jd_extractor)
    workflow.add_node("project_researcher", agent.project_researcher)
    workflow.add_node("tool_call_project_research", agent.tool_call_project_research)
    workflow.add_node("project_summarizer", agent.project_summarizer)
    workflow.add_node("project_formatter", agent.project_formatter)
    workflow.add_node("resume_scorer", agent.resume_scorer)
    workflow.add_node("resume_writer", agent.resume_writer)


    #edges
    workflow.add_edge(START, "jd_extractor")
    workflow.add_edge("jd_extractor", "project_researcher")
    workflow.add_edge("tool_call_project_research", "project_researcher")
    workflow.add_edge("project_summarizer", "project_formatter")
    workflow.add_edge("project_formatter", "resume_scorer")
    workflow.add_edge("resume_writer", "resume_scorer")

    #conditional edges
    workflow.add_conditional_edges("project_researcher", agent.router_project_research,
                                   {
                                       "tool_call_project_research": "tool_call_project_research",
                                       "project_summarizer": "project_summarizer"
                                   })
    workflow.add_conditional_edges("resume_scorer", agent.router_resume_writer,
                                   {
                                      "resume_writer": "resume_writer",
                                      END: END
                                   })

    compiled_workflow = workflow.compile()

    return compiled_workflow