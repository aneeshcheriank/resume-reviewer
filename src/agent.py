from src import prompts
from src.model import get_llm
from src.state import AgentState
from src import prompts
from src import inputs

def jd_extractor(state: AgentState):
    prompt = prompts.jd_keyword_extraction_prompt
    llm = get_llm()
    jd = inputs.get_jd()

    chain = prompt | llm
    response = chain.invoke({
        "job_description": jd
    })

    return response
