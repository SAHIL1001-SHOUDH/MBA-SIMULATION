from langchain_core.messages import HumanMessage
from models.v1.validations.conversation_state import ConversationState

def User_Node(state: ConversationState) -> ConversationState:
    """Process user interjection with proper message formatting"""
    if not state.pending_user_message:
        return state

    # Create proper HumanMessage object instead of dictionary
    user_message = HumanMessage(
        content=state.pending_user_message,
        additional_kwargs={
            "participant_role": "user"
        }
    )

    return ConversationState(
        messages=state.messages + [user_message],
        current_speaker="user",
        discussion_topic=state.discussion_topic,
        pending_user_message=None,
        user_interjection_allowed=False
    )