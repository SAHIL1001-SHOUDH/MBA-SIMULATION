from langchain.schema import AIMessage
from core.v1.agents.hr import hr_agent
from models.v1.validations.conversation_state import ConversationState


def Hr_Node(state: ConversationState) -> ConversationState:
    """Process HR's response with proper state management and error handling."""
    
    # Validate input state
    if not state.messages:
        raise ValueError("HR cannot respond to empty conversation history")

    try:
        # Get last message content safely
        last_message = state.messages[-1]
        last_message_content = last_message.content  # Use attribute access
        
        response = hr_agent.invoke({
            "input": f"Discussion Topic: {state.discussion_topic}\nLast Message: {last_message_content}",
            "chat_history": [msg.content for msg in state.messages]
        })
        
        # Extract content from different response types
        if isinstance(response, AIMessage):
            response_content = response.content
        elif isinstance(response, dict):
            response_content = response.get("output", "No HR response generated")
        else:
            response_content = str(response)
            
    except Exception as e:
        response_content = f"HR Error: {str(e)}"

    formatted_message = AIMessage(
        content=response_content,
        additional_kwargs={
            "participant_role": "hr",
        }
    )
    
    return ConversationState(
        messages=state.messages + [formatted_message],
        current_speaker="hr",
        discussion_topic=state.discussion_topic,
        pending_user_message=state.pending_user_message,
        user_interjection_allowed=True
    )
