from langchain.schema import AIMessage
from core.v1.agents.ceo import ceo_agent
from models.v1.validations.conversation_state import ConversationState
from utils.v1.shared_resources.message_queue import send_message
from utils.v1.workflow.interruption_check import execute_with_interruption_check
def _ceo_function(state: ConversationState) -> ConversationState:
    """The actual CEO agent function that processes the state."""
    chat_history = [
        {
            "role": msg.get("role", ""),
            "content": msg.get("content", ""),
            "type": msg.get("type", "")
        } for msg in state.messages
    ]

    current_topic = state.discussion_topic
    ceo_prompt = f"""
    Current discussion topic: {current_topic}
    
    Provide a strategic response considering the full conversation history.
    Contribute insights relevant to the ongoing discussion.
    """

    try:
        response = ceo_agent.invoke({
            "input": ceo_prompt,
            "chat_history": chat_history
        })
        
        # Extract content from different response types
        if isinstance(response, AIMessage):
            response_content = response.content
        elif isinstance(response, dict):
            response_content = response.get("output", "No response generated")
        else:
            response_content = str(response)

        state.messages.append({
            "role": "assistant",
            "content": response_content,
            "type": "ceo_response"
        })

        send_message({
            "role": "assistant",
            "content": response_content,
            "type": "ceo_response"
        })

        state.current_speaker = "ceo"
            
    except Exception as e:
        error_message = {
            "role": "system",
            "content": f"CEO response generation error: {str(e)}",
            "type": "error"
        }
        state.messages.append(error_message)
        send_message(error_message)

    return state

# Wrap CEO function with interruption check
def Ceo_Node(state: ConversationState) -> ConversationState:
    return execute_with_interruption_check(_ceo_function, state, "ceo")
