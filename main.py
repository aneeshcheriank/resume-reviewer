from src import agent
from src.state import AgentState

if __name__== "__main__":
    response = agent.jd_extractor(AgentState)
    print(response)