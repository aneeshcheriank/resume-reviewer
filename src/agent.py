from langgraph.graph import END

from src import prompts
from src.model import get_llm
from src.state import AgentState
from src import inputs
from src import schema
from src.utility import tool_call_node, router
from src import tools, config

def jd_extractor(state: AgentState):
    prompt = prompts.jd_keyword_extraction_prompt
    llm = get_llm()
    llm_with_structured_output = llm.with_structured_output(schema=schema.JDExtractorSchema)
    jd = inputs.get_jd()

    chain = prompt | llm_with_structured_output
    response = chain.invoke({
        "job_description": state['job_description']
    })
    output = response.model_dump()

    return {
        "jd": jd,
        "organization": output.get("organization", ""),
        "role": output.get("role", ""),
        "department": output.get("department", ""),
        "hard_skills": output.get("hard_skills", []),
        "soft_skills": output.get("soft_skills", []),
        "keywords": output.get("keywords", [])
    }

def project_researcher(state: AgentState):
    prompt = prompts.project_researcher_prompt
    llm = get_llm()
    llm_with_tools = llm.bind_tools([tools.search_tool])
    iteration = state["project_research_iteration"]
    
    if iteration < config.max_search_calls:
        chain = prompt | llm_with_tools
    else:
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

def project_formatter(state: AgentState):
    prompt = prompts.project_formatter_prompt
    llm = get_llm()
    llm_with_structured_output = llm.with_structured_output(schema.ProjectResearcher)
    last_history = state["research_history"][-1]

    chain = prompt | llm_with_structured_output
    response = chain.invoke({
        "summary": last_history
    })

    output = response.model_dump()

    return{
         "projects": output.get("projects"),
         "business_model": output.get("business_model"),
         "product_and_services": output.get("product_and_services"),
         "competition": output.get("competition")
    }

def resume_scorer(state: AgentState):
    prompt = prompts.resume_scoring_prompt
    llm = get_llm()
    llm_with_structured_output = llm.with_structured_output(schema.ResumeScore)

    chain = prompt | llm_with_structured_output
    response = chain.invoke({
        "resume": state["resume"],
        "hard_skills": state["hard_skills"],
        "soft_skills": state["soft_skills"],
        "keywords": state["keywords"]
    })

    output = response.model_dump()
    return {
        "resume_score": output.get("resume_score", 0),
        "detailed_score": output.get("detailed_score", {}),
        "details": output.get("details", "")
    }

def resume_writer(state: AgentState):
    prompt = prompts.resume_writer_prompt
    llm = get_llm()
    llm_with_structured_output = llm.with_structured_output(schema.ResumeWriter)

    chain = prompt | llm_with_structured_output
    response = chain.invoke({
        "resume": state["resume"],
        "hard_skills": state["hard_skills"],
        "soft_skills": state["soft_skills"],
        "keywords": state["keywords"],
        "resume_score": state["resume_score"],
        "scoring_details": state["details"],
        "detailed_score": state["detailed_score"],
        "resume_write_iteration": state["resume_write_iteration"] + 1
    })

    output = response.model_dump()
    return {
        "resume": output.get("resume", ""),
        "resume_modification_explanation": output.get("explanation", "")
    }

def router_resume_writer(state:AgentState):
    print(f"resume score: {state['resume_score']}")

    if state["resume_write_iteration"] >= config.max_resume_write_iteration:
        print(state["resume"])
        return END
    
    if state["resume_score"] < config.resume_matching_score:
        return "resume_writer"
    
    print(state["resume"])
    return END