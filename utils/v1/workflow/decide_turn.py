from langchain.schema import AIMessage
from langgraph.graph import END
from core.v1.agents.moderate_agent import moderator_agent
from models.v1.validations.conversation_state import ConversationState

def decide_next_speaker(state: ConversationState) -> str:
    """Determine which agent should speak next based on the conversation context."""
    # If we were interrupted, force next turn to go through moderator again
    if state.interrupted:
        return "moderator"
    

    # Use your moderator agent to decide the next speaker
    moderator = moderator_agent
    chat_history = state.messages
    current_topic = state.discussion_topic
    last_speaker = state.current_speaker

    print("current topic",current_topic)
    print("last speaker",last_speaker)

    decision_prompt = f"""
        Current discussion topic: {current_topic}
        Last speaker: {last_speaker}

        Based on the conversation history and the current topic, who should speak next?
        Choose ONLY ONE of these exact options:

        Valid Options (respond with exactly these words):
        - ceo: Strategic decisions, vision alignment, budget approvals
        - product_manager: Product details, feature prioritization, roadmap
        - hr: Team composition, hiring needs, organizational concerns
        - end_discussion: Conversation conclusion

        IMPORTANT RESPONSE RULES:
        1. You MUST respond with ONLY the exact option word (e.g., "ceo")
        2. Do NOT include explanations, punctuation, or additional text
        3. If unsure, default to "end_discussion"

        Your response must be exactly one word from the valid options list.
    """

    routing_response = moderator.invoke(
        {
            "input": (
                "You are deciding which specialist should address the current discussion point.\n"
                f"User prompt: {decision_prompt}"
            ),
            "chat_history": chat_history,
        }
    )
    print("response" , routing_response)

    if isinstance(routing_response, AIMessage):
        next_speaker = routing_response.content.lower().strip()
    elif isinstance(routing_response, dict):
        next_speaker = routing_response.get("output", "").lower().strip()
    else:
        next_speaker = str(routing_response).lower().strip()

    first_word = next_speaker.split()[0] if next_speaker else ""
    valid_roles = {"ceo", "product_manager", "hr", "end_discussion"}
    print(first_word)
    
    if first_word in valid_roles:
        return first_word
    return "end_discussion"