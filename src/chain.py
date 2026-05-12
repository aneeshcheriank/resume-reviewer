from langgraph.graph import StateGraph, START, END
from src.state import AgentState

def built_graph():
    workflow = StateGraph(AgentState)

    #nodes

    #edges

    #conditional edges

    compiled_workflow = workflow.compile()

    return compiled_workflow