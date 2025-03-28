from utils.v1.workflow.conversation_manager import ConversationManager
import gradio as gr
import logging

manager = None

def start_conversation(topic):
    global manager
    try:
        manager = ConversationManager(topic)
        initial_response = manager.start_conversation()
        return initial_response
    except Exception as e:
        return f"Error starting conversation: {e}"

def continue_conversation():
    global manager
    if manager is None:
        return "No active conversation. Please start a conversation first."
    
    try:
        return next(manager.conversation_generator)
    except StopIteration:
        return "Conversation Ended."
    except Exception as e:
        return f"Error continuing conversation: {e}"

def handle_human_input(message, current_log):
    global manager
    if manager is None:
        return "No active conversation. Please start a conversation first."
    
    try:
        human_response = f"You: {message}"
        
        # Handle human interjection and get agent response
        agent_response = manager.handle_human_interjection(message)
        
        # Try to get updated log from conversation generator
        try:
            updated_log = next(manager.conversation_generator)
        except StopIteration:
            updated_log = "Conversation Ended."
        
        # Combine logs
        combined = current_log + "\n" + human_response + "\n" + f"Agent: {agent_response}" + "\n" + updated_log
        
        return combined
    except Exception as e:
        return f"Error handling input: {e}"

# Create Gradio interface
with gr.Blocks() as demo:
    gr.Markdown("## Multi-Agent Discussion")
    
    # Inputs
    topic_input = gr.Textbox(label="Enter Discussion Topic", interactive=True)
    interjection_input = gr.Textbox(label="Your Interjection", interactive=True)
    
    # Buttons
    start_btn = gr.Button("Start Conversation")
    interject_btn = gr.Button("Interject")
    continue_btn = gr.Button("Continue Conversation")
    
    # Conversation log
    chatbox = gr.Textbox(label="Conversation Log", interactive=False, lines=15)
    
    # Event handlers
    start_btn.click(start_conversation, inputs=topic_input, outputs=chatbox)
    interject_btn.click(handle_human_input, inputs=[interjection_input, chatbox], outputs=chatbox)
    continue_btn.click(continue_conversation, inputs=None, outputs=chatbox)

# Launch the demo
demo.launch()