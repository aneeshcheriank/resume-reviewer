from langchain_core.messages import ToolMessage

from src.state import AgentState

def tool_call_node(history, iter_name, tool_mapping):
    # This returns a function that LangGraph will call later with the actual state
    def node(state: AgentState):
        # Now 'state' is the actual data (dict), not the class
        last_state = state[history][-1]
        iterations = state[iter_name] + 1

        print(f"Executing tool call for {history}")

        tool_messages = []
        for tool_call in last_state.tool_calls:
            name = tool_call.get("name")
            args = tool_call.get("args")
            
            if name in tool_mapping:
                tool_response = tool_mapping[name].invoke(args)
                tool_messages.append(
                    ToolMessage(
                        content=str(tool_response),
                        tool_call_id=tool_call.get("id")
                    )
                )

        return {
            history: tool_messages,
            iter_name: iterations
        }
    return node

def router(history, map: dict):
    def node(state: AgentState):
        last_state = state[history][-1]
    
        if last_state.tool_calls:
            return map.get("tool_call")
        
        else:
            return map.get("default")
    return node