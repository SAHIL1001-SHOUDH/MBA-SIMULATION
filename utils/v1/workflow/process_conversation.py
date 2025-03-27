from langchain.schema import HumanMessage
from models.v1.validations.conversation_state import ConversationState

def process_conversation_step(stream, step_count, messages):
    """Process conversation steps and build output incrementally."""
    for idx, step in enumerate(stream):
        if idx < step_count:
            print(idx, "skip")
            continue

        node_name = list(step.keys())[0]
        current_state = step[node_name]

        if not isinstance(current_state, ConversationState):
            current_state = ConversationState(
                messages=current_state.get('messages', []),
                current_speaker=current_state.get('current_speaker', 'moderator'),
                discussion_topic=current_state.get('discussion_topic', ''),
                pending_user_message=current_state.get('pending_user_message', None),
                user_interjection_allowed=current_state.get('user_interjection_allowed', False)
            )

        # Handle pending user messages
        if current_state.pending_user_message:
            formatted_message = HumanMessage(
                content=current_state.pending_user_message,
                additional_kwargs={"participant_role": "user"}
            )
            messages.append(formatted_message)
            current_state.pending_user_message = None

        # Add participant messages
        if node_name != "moderator" and current_state.messages:
            last_message = current_state.messages[-1].content
            formatted_message = HumanMessage(
                content=last_message,
                additional_kwargs={"participant_role": node_name}
            )
            messages.append(formatted_message)

        # Yield after each step with updated messages
        yield step, idx+1, "\n".join(msg.content for msg in messages), current_state.user_interjection_allowed
