from langchain_core.messages import ToolMessage

from src.state import AgentState

def tool_call_node(state: AgentState, history, iter_name, tool_mapping):
    # this node will handle the tool call and update the state accordingly
    last_state = state[history][-1]
    # increment the iteration count
    iterations = state[iter_name] + 1

    print("tool_call")

    tool_messages = []
    for tool_call in last_state.tool_calls:

        name = tool_call.get("name")
        args = tool_call.get("args")
        
        if name in tool_mapping:
            tool_response = tool_mapping[name].invoke(args) #invoke expect dictionary as input
            tool_messages.append(
                ToolMessage(
                    content = str(tool_response),
                    tool_call_id = tool_call.get("id")
                )
            )

    return {
        history: tool_messages, #the tool_messages is a list
        iter_name: iterations
    }