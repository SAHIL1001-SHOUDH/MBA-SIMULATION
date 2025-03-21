import gradio as gr
import time
from models.v1.validations.conversation_state import ConversationState
from core.v1.graph.discussion_flow import build_conversation_graph

def run_conversation(topic: str):
    initial_state = ConversationState(
        messages=[{"role": "system", "content": f"Discussion started on {topic}"}],
        current_speaker="moderator",
        discussion_topic=topic,
    )

    conversation_graph = build_conversation_graph()
    conversation_output = []

    for step in conversation_graph.stream(initial_state):
        node_name = list(step.keys())[0]
        print(node_name)
        state = step[node_name]


        if node_name != "moderator":
            last_message = state['messages'][-1]['content']
            formatted_message = f"{node_name.upper()}: {last_message}"
            conversation_output.append(formatted_message)
            yield "\n".join(conversation_output)

        time.sleep(0.5)

iface = gr.Interface(
    fn=run_conversation,
    inputs=gr.Textbox(
        label="Discussion Topic", value="Q2 Product Roadmap Prioritization"
    ),
    outputs=gr.Textbox(label="Conversation Log", lines=10),
    title="Conversation Graph Simulator",
    description="Enter a discussion topic to simulate the conversation flow using the conversation graph.",
)

if __name__ == "__main__":
    iface.launch()