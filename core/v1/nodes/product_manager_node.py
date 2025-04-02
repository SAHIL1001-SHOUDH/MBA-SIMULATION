from langchain.schema import AIMessage
from core.v1.agents.product_manager import pm_agent
from models.v1.validations.conversation_state import ConversationState
from utils.v1.shared_resources.message_queue import send_message
from utils.v1.workflow.interruption_check import execute_with_interruption_check
def _product_manager_function(state: ConversationState) -> ConversationState:
    """The actual Product Manager agent function that processes the state."""
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
    
    Provide a product perspective considering the full conversation history.
    Address features, roadmap, and user-centered aspects of the discussion.
    """

    try:
        response = pm_agent.invoke({
            "input": pm_prompt,
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
            "type": "product_manager_response"
        })

        send_message({
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
        send_message(error_message)

    return state

# Wrap Product Manager function with interruption check
def Product_Manager_Node(state: ConversationState) -> ConversationState:
    return execute_with_interruption_check(_product_manager_function, state, "product_manager")