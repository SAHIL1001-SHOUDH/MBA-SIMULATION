from langchain.schema import AIMessage
from core.v1.agents.ceo import ceo_agent
from models.v1.validations.conversation_state import ConversationState

def Ceo_Node(state: ConversationState) -> ConversationState:
    """Process CEO's response with proper state management."""
    
    # Validate input state
    if not state.messages:
        raise ValueError("CEO cannot respond to empty conversation history")
    
    try:
        # Access message content using .content attribute
        last_message_content = state.messages[-1].content
        
        response = ceo_agent.invoke({
            "input": f"Discussion Topic: {state.discussion_topic}\nLast Message: {last_message_content}",
            "chat_history": [msg.content for msg in state.messages]  # Convert to simple strings
        })
        
        # Extract content from different response types
        if isinstance(response, AIMessage):
            response_content = response.content
        elif isinstance(response, dict):
            response_content = response.get("output", "No response generated")
        else:
            response_content = str(response)
            
    except Exception as e:
        response_content = f"CEO Error: {str(e)}"
    
    # Use AIMessage for CEO responses instead of HumanMessage
    formatted_message = AIMessage(
        content=response_content,
        additional_kwargs={
            "participant_role": "ceo" 
        }
    )
    
    return ConversationState(
        messages=state.messages + [formatted_message],
        current_speaker="ceo",
        discussion_topic=state.discussion_topic,
        pending_user_message=state.pending_user_message,
        user_interjection_allowed=True
    )