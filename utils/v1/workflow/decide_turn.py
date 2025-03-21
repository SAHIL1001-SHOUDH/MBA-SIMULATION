from core.v1.agents.moderate_agent import moderator_agent
from models.v1.validations.conversation_state import ConversationState


def decide_next_speaker(state: ConversationState) -> str:
    """Determine which agent should speak next based on the conversation context."""
    moderator = moderator_agent
    chat_history = state.messages
    current_topic = state.discussion_topic
    last_speaker = state.current_speaker

    # Create a prompt that helps the moderator decide the next speaker
    decision_prompt = f"""
    Current discussion topic: {current_topic}
    Last speaker: {last_speaker}
    
    Based on the conversation history and the current topic, who should speak next?
    
    Options:
    - "ceo": For strategic decisions, vision alignment, or budget approvals
    - "product_manager": For product details, feature prioritization, or roadmap discussions
    - "hr": For team composition, hiring needs, or organizational concerns
    - "end_discussion": If the conversation has reached a natural conclusion
    
    Provide just the role name as your answer.
    """

    # Ask the moderator LLM who should speak next
    routing_response = moderator.invoke(
        {
            "input": (
                "You are deciding which specialist should address the current discussion point.\n"
                f"User prompt: {decision_prompt}"
            ),
            "chat_history": chat_history,
        }
    )

    if isinstance(routing_response, dict) and "output" in routing_response:
        next_speaker = routing_response["output"].lower().strip()
    else:
        next_speaker = str(routing_response).lower().strip()

    # Map the response to one of our valid options
    if "ceo" in next_speaker:
        return "ceo"
    elif "product" in next_speaker or "pm" in next_speaker:
        return "product_manager"
    elif "hr" in next_speaker:
        return "hr"
    else:
        return "end_discussion"
