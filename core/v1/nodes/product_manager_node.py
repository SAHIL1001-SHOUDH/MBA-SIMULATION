from langchain.schema import AIMessage
from core.v1.agents.product_manager import pm_agent
from models.v1.validations.conversation_state import ConversationState


def Product_Manager_Node(state: ConversationState) -> ConversationState:
    """Process Product Manager's response with proper state management and error handling."""

    if not state.messages:
        raise ValueError("Product Manager cannot respond to empty conversation history")
    
    try:

        last_message = state.messages[-1]
        last_message_content = last_message.content

        response = pm_agent.invoke({
            "input": f"Discussion Topic: {state.discussion_topic}\nLast Message: {last_message_content}",
            "chat_history": [msg.content for msg in state.messages]
        })

        if isinstance(response, AIMessage):
            response_content = response.content
        elif isinstance(response, dict):
            response_content = response.get("output", "No PM response generated")
        else:
            response_content = str(response)
            
    except Exception as e:
        response_content = f"Product Manager Error: {str(e)}"

    formatted_message = AIMessage(
        content=response_content,
        additional_kwargs={
            "participant_role": "product_manager"  # Store role in metadata
        }
    )
    
    return ConversationState(
        # Wrap in list to properly extend messages sequence
        messages=state.messages + [formatted_message],
        current_speaker="product_manager",
        discussion_topic=state.discussion_topic,
        pending_user_message=state.pending_user_message,
        user_interjection_allowed=True
    )