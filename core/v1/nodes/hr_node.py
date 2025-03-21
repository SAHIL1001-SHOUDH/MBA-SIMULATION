from core.v1.agents.hr import hr_agent
from models.v1.validations.conversation_state import ConversationState


def Hr_Node(state: ConversationState):
    messages = state.messages
    if not messages:
        raise ValueError("No messages found in state.")

    response = hr_agent.invoke(
        {"input": messages[-1]["content"], "chat_history": messages}
    )

    if isinstance(response, dict) and "output" in response:
        response_content = response["output"]
    else:
        response_content = str(response)

    return ConversationState(
        messages=messages + [{"role": "assistant", "content": response_content}],
        current_speaker="hr",
        discussion_topic=state.discussion_topic,
    )
