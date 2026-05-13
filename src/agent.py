from src import prompts
from src.model import get_llm
from src.state import AgentState
from src import inputs
from src import schema
from src.utility import tool_call_node, router
from src import tools

def jd_extractor(state: AgentState):
    prompt = prompts.jd_keyword_extraction_prompt
    llm = get_llm()
    llm_with_structured_output = llm.with_structured_output(schema=schema.JDExtractorSchema)
    jd = inputs.get_jd()

    chain = prompt | llm_with_structured_output
    response = chain.invoke({
        "job_description": state['job_description'],
        "query": state["query"]
    })
    output = response.model_dump()

    return {
        "jd": jd,
        "org": output.get("org", ""),
        "role": output.get("role", ""),
        "department": output.get("department", ""),
        "hard_skills": output.get("hard_skills", ""),
        "soft_skills": output.get("soft_skills", ""),
        "key_words": output.get("key_words", "")
    }

def project_researcher(state: AgentState):
    prompt = prompts.project_researcher_prompt
    llm = get_llm()

    chain = prompt | llm
    response = chain.invoke({
        "organization": state["organization"],
        "department": state["department"]
    })

    return{
        "research_history": [response]
    }

tool_call_project_research = tool_call_node("research_history", "project_research_iteration", tools.project_research_tool_mapping)
router_project_research = router("research_history", map={
    "tool_call": "tool_call_project_research", "default": "project_summarizer"
})

def project_summarizer(state: AgentState):
    prompt = prompts.summary_research_prompt
    llm = get_llm()

    chain = prompt | llm
    response = chain.invoke({
        "chat_history": state["research_history"]
    })

    return{
        "research_history": [response]
    }