from langchain.schema import AIMessage
from core.v1.agents.hr import hr_agent
from models.v1.validations.conversation_state import ConversationState
from utils.v1.shared_resources.message_queue import send_message
from utils.v1.workflow.interruption_check import execute_with_interruption_check
def _hr_function(state: ConversationState) -> ConversationState:
    """The actual HR agent function that processes the state."""
    chat_history = [
        {
            "role": msg.get("role", ""),
            "content": msg.get("content", ""),
            "type": msg.get("type", "")
        } for msg in state.messages
    ]

    current_topic = state.discussion_topic
    hr_prompt = f"""
    Current discussion topic: {current_topic}
    
    Provide an HR perspective considering the full conversation history.
    Address organizational and people-related aspects of the discussion.
    """

    try:
        response = hr_agent.invoke({
            "input": hr_prompt,
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
            "type": "hr_response"
        })

        send_message({
            "role": "assistant",
            "content": response_content,
            "type": "hr_response"
        })

        state.current_speaker = "hr"
            
    except Exception as e:
        error_message = {
            "role": "system",
            "content": f"HR response generation error: {str(e)}",
            "type": "error"
        }
        state.messages.append(error_message)
        send_message(error_message)

    return state

# Wrap HR function with interruption check
def Hr_Node(state: ConversationState) -> ConversationState:
    return execute_with_interruption_check(_hr_function, state, "hr")