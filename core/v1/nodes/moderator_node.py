from core.v1.agents.moderate_agent import moderator_agent
from models.v1.validations.conversation_state import ConversationState


def Moderator_Node(state: ConversationState):
    
    return ConversationState(
        messages=state.messages,
        current_speaker=state.current_speaker,
        discussion_topic=state.discussion_topic,
        pending_user_message=state.pending_user_message,
        user_interjection_allowed=True
    )
