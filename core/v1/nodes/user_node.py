from core.v1.agents.moderate_agent import moderator_agent
from models.v1.validations.conversation_state import ConversationState


def Human_Response_Node(state: ConversationState):
    """
    Process human interjections and manage conversation flow.
    
    Args:
        state (ConversationState): Current conversation state
    
    Returns:
        ConversationState: Updated conversation state
    """
    # If there are no interjections, return state unchanged
    if not state.human_interjections:
        return state

    latest_interjection = state.human_interjections[-1]

    response_integrator = moderator_agent
    integration_response = response_integrator.invoke({
        "input": f"Help integrate this human interjection into the conversation: {latest_interjection.message}",
        "chat_history": state.messages
    })

    # Clear processed interjections
    state.human_interjections = []

    return state