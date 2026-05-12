from src import prompts
from src.model import get_llm
from src.state import AgentState
from src import prompts
from src import inputs
from src import schema

def jd_extractor(state: AgentState):
    prompt = prompts.jd_keyword_extraction_prompt
    llm = get_llm()
    llm_with_structured_output = llm.with_structured_output(schema=schema.JDExtractorSchema)
    jd = inputs.get_jd()

    chain = prompt | llm_with_structured_output
    response = chain.invoke({
        "job_description": jd
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
