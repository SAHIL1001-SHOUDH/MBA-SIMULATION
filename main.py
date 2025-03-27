import gradio as gr
from langchain_core.messages import SystemMessage
from models.v1.validations.conversation_state import ConversationState
from core.v1.graph.discussion_flow import build_conversation_graph
from utils.v1.workflow.user_interjection import add_user_interjection
from utils.v1.workflow.process_conversation import process_conversation_step



def run_conversation(topic: str, interjection: str = None, state: dict = None):
    """Run conversation with proper state initialization"""
    # Initialize state if needed
    if state is None or not state.get("stream"):
        initial_state = ConversationState(
            messages=[SystemMessage(content=f"Discussion started on {topic}")],
            current_speaker="moderator",
            discussion_topic=topic,
            user_interjection_allowed=False
        )
        return {
            "stream": build_conversation_graph().stream(initial_state),
            "messages": [],
            "step_count": 0,
            "state": initial_state
        }, "", False

    stream = state["stream"]
    messages = state["messages"]
    step_count = state["step_count"]
    current_state = state["state"]

    if interjection and current_state.user_interjection_allowed:
        current_state = add_user_interjection(current_state, interjection)
        state["state"] = current_state

    try:
        for step, new_step_count, output, allow_interrupt in process_conversation_step(
            stream, step_count, messages
        ):
            state["step_count"] = new_step_count
            state["state"] = step[list(step.keys())[0]]
            return state, output, allow_interrupt
    except StopIteration:
        return state, output, False

    return state, output, False

def start_conversation(topic, state):
    new_state, _, _ = run_conversation(topic)
    return new_state

def process_next_step(state):
    if state and state.get("stream"):
        updated_state, output, allow_interrupt = run_conversation(None, state=state)
        return updated_state, output, gr.update(visible=allow_interrupt)
    return state, "", False

iface = gr.Blocks(title="State-Managed Conversation")

with iface:
    gr.Markdown("## 💼 Executive Discussion Panel")
    state = gr.State()
    
    with gr.Row():
        topic_input = gr.Textbox(label="Discussion Topic", value="Q3 Market Expansion Strategy")
        start_btn = gr.Button("Start Meeting", variant="primary")
    
    interjection_input = gr.Textbox(label="Your Input", visible=False)
    interjection_btn = gr.Button("Send", variant="secondary", visible=False)
    
    conversation_log = gr.Textbox(label="Meeting Transcript", interactive=False)
    
    start_btn.click(
        start_conversation,
        [topic_input, state],
        [state]
    ).then(
        process_next_step,
        [state],
        [state, conversation_log, interjection_input]
    ).then(
        process_next_step,
        [state],
        [state, conversation_log, interjection_input],
    )
    
    interjection_btn.click(
        process_next_step,
        [state, interjection_input],
        [state, conversation_log, interjection_input]
    )

if __name__ == "__main__":
    iface.launch()