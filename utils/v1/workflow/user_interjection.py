from models.v1.validations.conversation_state import ConversationState

def add_user_interjection(conversation_state: ConversationState, user_message: str) -> ConversationState:
    """
    Add a user interjection to the conversation state.
    
    Args:
        conversation_state (ConversationState): Current conversation state
        user_message (str): Message to be interjected
    
    Returns:
        ConversationState: Updated conversation state with pending user message
    """
    if not conversation_state['pending_user_message'] and conversation_state['user_interjection_allowed']:
        return ConversationState(
            messages=conversation_state['messages'],
            current_speaker=conversation_state['current_speaker'],
            discussion_topic=conversation_state['discussion_topic'],
            pending_user_message=user_message,
            user_interjection_allowed=False
        )
    return conversation_state