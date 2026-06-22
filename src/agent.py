from langgraph.graph import END

from src import prompts
from src.model import get_llm
from src.state import AgentState
from src import schema
from src.utility import tool_call_node, router
from src import tools, config


def jd_extractor(state: AgentState):
    prompt = prompts.jd_keyword_extraction_prompt
    llm = get_llm()
    llm_with_structured_output = llm.with_structured_output(schema=schema.JDExtractorSchema)

    chain = prompt | llm_with_structured_output
    response = chain.invoke({
        "job_description": state['job_description']
    })
    output = response.model_dump()

    return {
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

    return {
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

    return {
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

    return {
         "projects": output.get("important_projects"),
         "business_model": output.get("business_model"),
         "product_and_services": output.get("product_and_services"),
         "competition": output.get("competition")
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
        "business_model": state.get("business_model", ""),
        "product_and_services": state.get("product_and_services", ""),
        "competition": state.get("competition", ""),
        "projects": state.get("projects", []),
    })

    output = response.model_dump()
    return {
        "enhanced_resume": output.get("resume", ""),
        "resume_modification_explanation": output.get("explanation", ""),
    }


def cover_letter_writer(state: AgentState):
    # Short-circuit if no cover letter was provided
    if not state.get("cover_letter", "").strip():
        return {
            "enhanced_cover_letter": "",
            "cover_letter_modification_explanation": "No cover letter provided.",
        }

    prompt = prompts.cover_letter_writer_prompt
    llm = get_llm()
    llm_with_structured_output = llm.with_structured_output(schema.CoverLetterWriter)

    chain = prompt | llm_with_structured_output
    response = chain.invoke({
        "cover_letter": state["cover_letter"],
        "role": state["role"],
        "organization": state["organization"],
        "hard_skills": state["hard_skills"],
        "soft_skills": state["soft_skills"],
        "keywords": state["keywords"],
        "business_model": state.get("business_model", ""),
        "product_and_services": state.get("product_and_services", ""),
        "competition": state.get("competition", ""),
        "projects": state.get("projects", []),
    })

    output = response.model_dump()
    return {
        "enhanced_cover_letter": output.get("cover_letter", ""),
        "cover_letter_modification_explanation": output.get("explanation", ""),
    }
