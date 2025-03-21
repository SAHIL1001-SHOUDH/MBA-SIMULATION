from core.v1.agents.moderate_agent import moderator_agent
from models.v1.validations.conversation_state import ConversationState


def Moderator_Node(state: ConversationState):
    moderator = moderator_agent

    messages = state.messages
    discussion_topic = state.discussion_topic

    response = moderator.invoke(
        {
            "input": f"Analyze the conversation and decide what to do next.\n\nDiscussion topic: {discussion_topic}",
            "chat_history": messages ,
        }
    )

    if isinstance(response, dict) and "output" in response:
        response_content = response["output"]
    else:
        response_content = str(response)

    return ConversationState(
        messages=messages + [{"role": "assistant", "content": response_content}],
        current_speaker=state.current_speaker,
        discussion_topic=state.discussion_topic,
    )
