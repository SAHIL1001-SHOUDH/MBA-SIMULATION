from models.v1.validations.conversation_state import ConversationState
from utils.v1.shared_resources.message_queue import send_message
from utils.v1.shared_resources.human_flag import interjection_control

def Moderator_Node(state: ConversationState) -> ConversationState:
    """Process moderator's decision with proper state management."""
    if interjection_control.check_for_interruption():
        user_input = interjection_control.get_and_clear_interruption()
        if user_input:
            state.add_human_interjection(user_input)
            send_message({
                "role": "human",
                "content": user_input,
                "type": "interjection"
            })
            state.interrupted = True
    
    # Reset the interruption flag
    state.interrupted = False
    return state
