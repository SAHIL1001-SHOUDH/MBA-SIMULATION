from utils.v1.shared_resources.human_flag import interjection_control
from utils.v1.shared_resources.message_queue import send_message
def execute_with_interruption_check(agent_function, state, agent_name):
    """
    Wrapper that allows for interruption during agent execution.
    If interrupted, it will update the state and return early.
    """
    # Check for interruption before processing
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
            return state
    
    # Execute the normal agent function
    return agent_function(state)