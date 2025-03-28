from langchain.schema import AIMessage
from core.v1.agents.product_manager import pm_agent
from models.v1.validations.conversation_state import ConversationState

def Product_Manager_Node(state: ConversationState) -> ConversationState:
    """Process Product Manager's response with proper state management."""

    chat_history = [
        {
            "role": msg.get("role", ""),
            "content": msg.get("content", ""),
            "type": msg.get("type", "")
        } for msg in state.messages
    ]

    current_topic = state.discussion_topic
    pm_prompt = f"""
    Current discussion topic: {current_topic}
    
    Provide a product-related response considering the full conversation history.
    Contribute insights relevant to product strategy, features, or development.
    """

    try:
        response = pm_agent.invoke({
            "input": pm_prompt,
            "chat_history": chat_history
        })
        
        # Extract content from response
        if isinstance(response, AIMessage):
            response_content = response.content
        elif isinstance(response, dict):
            response_content = response.get("output", "No PM response generated")  # KEY CHANGED HERE
        else:
            response_content = str(response)

        state.messages.append({
            "role": "assistant",
            "content": response_content,
            "type": "product_manager_response"
        })

        state.current_speaker = "product_manager"
            
    except Exception as e:
        error_message = {
            "role": "system",
            "content": f"Product Manager response generation error: {str(e)}",
            "type": "error"
        }
        state.messages.append(error_message)

    return state