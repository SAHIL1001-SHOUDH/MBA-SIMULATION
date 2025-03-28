from langchain.schema import AIMessage
from core.v1.agents.hr import hr_agent
from models.v1.validations.conversation_state import ConversationState

def Hr_Node(state: ConversationState) -> ConversationState:
    """Process HR's response with proper state management."""

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
    
    Provide an HR-related response considering the full conversation history.
    Contribute insights relevant to team dynamics, personnel, or organizational structure.
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
            response_content = response.get("output", "No HR response generated")
        else:
            response_content = str(response)

        state.messages.append({
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

    return state