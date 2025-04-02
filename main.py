import gradio as gr
import threading
import logging
import traceback
import sys
from utils.v1.shared_resources.human_flag import interjection_control
from models.v1.validations.conversation_state import ConversationState
from core.v1.graph.discussion_flow import build_conversation_graph
from utils.v1.shared_resources.message_queue import send_message,message_queue

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("debug.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("multi_agent_chat")

def create_gradio_interface():
    conversation_thread = None
    graph_running = threading.Event()
    chat_history_data = []  # Maintain chat history locally
    
    with gr.Blocks() as demo:
        debug_output = gr.Textbox(label="Debug Output", interactive=False, lines=5)
        chat_history = gr.Chatbot(height=600, label="Multi-Agent Discussion")
        
        with gr.Row():
            user_input = gr.Textbox(
                placeholder="Type your message here to interrupt at any time...", 
                label="Your Input", 
                scale=9
            )
            submit_btn = gr.Button("Interrupt", scale=1)
        
        topic_input = gr.Textbox(
            placeholder="Enter discussion topic...", 
            label="Discussion Topic"
        )
        
        with gr.Row():
            start_btn = gr.Button("Start Discussion", scale=1)
            stop_btn = gr.Button("Stop Discussion", scale=1)
        
        def update_debug(message):
            logger.debug(message)
            return message
        
        def on_user_interrupt(message):
            try:
                update_debug(f"User interrupt with message: {message}")
                
                if not message:
                    update_debug("Empty message, ignoring interrupt")
                    return ""
                    
                if not graph_running.is_set():
                    update_debug("Graph not running, ignoring interrupt")
                    return message
                
                update_debug("Checking if interjection_control exists")
                if 'interjection_control' not in globals():
                    update_debug("interjection_control not found in globals")
                    return f"ERROR: interjection_control not defined. Message: {message}"
                
                update_debug(f"Calling interjection_control.interrupt({message})")
                interjection_control.interrupt(message)
                update_debug("Interrupt sent successfully")
                return ""
            except Exception as e:
                error_msg = f"Error in interrupt: {str(e)}\n{traceback.format_exc()}"
                update_debug(error_msg)
                return f"ERROR: {str(e)}"
        
        def on_start_discussion(topic):
            nonlocal conversation_thread
            nonlocal chat_history_data
            
            update_debug(f"Starting discussion with topic: {topic}")
            
            if not topic:
                update_debug("Empty topic, aborting")
                return chat_history_data, "Please enter a discussion topic"
            
            if graph_running.is_set():
                update_debug("Graph already running, ignoring start request")
                return chat_history_data, topic
            
            # Clear the chat history
            chat_history_data = []
            update_debug("Chat history cleared")
            
            try:
                # Check if ConversationState exists
                update_debug("Checking if ConversationState exists")
                if 'ConversationState' not in globals():
                    error_msg = "ConversationState class not found in globals"
                    update_debug(error_msg)
                    chat_history_data.append(["system", f"ERROR: {error_msg}"])
                    return chat_history_data, topic
                
                # Initialize the state
                update_debug(f"Creating initial state with topic: {topic}")
                initial_state = ConversationState(discussion_topic=topic)
                
                # Check if messages attribute exists
                if not hasattr(initial_state, 'messages'):
                    error_msg = "ConversationState has no 'messages' attribute"
                    update_debug(error_msg)
                    chat_history_data.append(["system", f"ERROR: {error_msg}"])
                    return chat_history_data, topic
                
                system_msg = {
                    "role": "system",
                    "content": f"Starting discussion on topic: {topic}",
                    "type": "system_message"
                }
                initial_state.messages.append(system_msg)
                update_debug("Initial message added to state.messages")
                
                # Add initial message to the chat history
                chat_history_data.append(["system", system_msg["content"]])
                update_debug("Initial message added to chat_history_data")
                
                # Start the graph in a separate thread
                def run_graph():
                    update_debug("Graph thread started")
                    graph_running.set()
                    try:
                        update_debug("Checking if build_conversation_graph exists")
                        if 'build_conversation_graph' not in globals():
                            error_msg = "build_conversation_graph function not found in globals"
                            update_debug(error_msg)
                            send_message({
                                "role": "system",
                                "content": f"ERROR: {error_msg}",
                                "type": "system_message"
                            })
                            return
                        
                        update_debug("Building conversation graph")
                        conversation_graph = build_conversation_graph()
                        update_debug(f"Graph built: {type(conversation_graph)}")
                        
                        welcome_msg = {
                            "role": "system",
                            "content": f"Discussion has started. Type a message and click 'Interrupt' at any time to join the conversation.",
                            "type": "system_message"
                        }
                        update_debug("Sending welcome message")
                        send_message(welcome_msg)
                        
                        update_debug("Invoking conversation graph")
                        result = conversation_graph.invoke(initial_state)
                        update_debug(f"Graph completed with result: {result}")
                    except Exception as e:
                        error_msg = f"Error in graph: {str(e)}\n{traceback.format_exc()}"
                        update_debug(error_msg)
                        send_message({
                            "role": "system",
                            "content": f"ERROR: {str(e)}",
                            "type": "system_message"
                        })
                    finally:
                        graph_running.clear()
                        update_debug("Graph stopped")
                        send_message({
                            "role": "system",
                            "content": "Discussion has ended.",
                            "type": "system_message"
                        })
                
                update_debug("Creating graph thread")
                conversation_thread = threading.Thread(target=run_graph, daemon=True)
                update_debug("Starting graph thread")
                conversation_thread.start()
                update_debug("Graph thread started successfully")
                
                return chat_history_data, topic
            except Exception as e:
                error_msg = f"Error starting discussion: {str(e)}\n{traceback.format_exc()}"
                update_debug(error_msg)
                chat_history_data.append(["system", f"ERROR: {str(e)}"])
                return chat_history_data, topic
        
        def on_stop_discussion():
            update_debug("Stop discussion requested")
            if graph_running.is_set():
                try:
                    update_debug("Checking if interjection_control exists")
                    if 'interjection_control' not in globals():
                        error_msg = "interjection_control not found in globals"
                        update_debug(error_msg)
                        send_message({
                            "role": "system",
                            "content": f"ERROR: {error_msg}",
                            "type": "system_message"
                        })
                        return None
                    
                    # Signal through an interruption that we want to end
                    update_debug("Sending END_DISCUSSION interrupt")
                    interjection_control.interrupt("END_DISCUSSION")
                    update_debug("END_DISCUSSION interrupt sent")
                    
                    send_message({
                        "role": "system",
                        "content": "Stopping the discussion...",
                        "type": "system_message"
                    })
                except Exception as e:
                    error_msg = f"Error stopping discussion: {str(e)}\n{traceback.format_exc()}"
                    update_debug(error_msg)
                    send_message({
                        "role": "system",
                        "content": f"ERROR: {str(e)}",
                        "type": "system_message"
                    })
            else:
                update_debug("Graph not running, nothing to stop")
            return None
        
        def update_chat():
            nonlocal chat_history_data
            try:
                # Debug message queue state
                update_debug(f"Message queue event state: {message_queue.new_message_event.is_set()}")
                update_debug(f"Queue approximate size: {message_queue.queue.qsize()}")
                
                # Check if there are new messages
                if message_queue.new_message_event.is_set():
                    update_debug("New messages available, retrieving")
                    new_messages = message_queue.get_messages()
                    update_debug(f"Retrieved {len(new_messages)} new messages")
                    
                    for msg in new_messages:
                        role = msg.get("role", "")
                        content = msg.get("content", "")
                        update_debug(f"Processing message - Role: {role}, Content: {content[:30]}...")
                        chat_history_data.append([role, content])
                    
                    update_debug(f"Chat history now has {len(chat_history_data)} messages")
                    return chat_history_data
                else:
                    update_debug("No new messages")
                return None
            except Exception as e:
                error_msg = f"Error updating chat: {str(e)}\n{traceback.format_exc()}"
                update_debug(error_msg)
                chat_history_data.append(["system", f"ERROR: {str(e)}"])
                return chat_history_data
        
        def get_debug_log():
            try:
                with open("debug.log", "r") as f:
                    log_lines = f.readlines()
                    # Get the last 5 lines
                    return "".join(log_lines[-5:])
            except Exception as e:
                return f"Error reading log: {str(e)}"
        
        submit_btn.click(
            on_user_interrupt, 
            inputs=[user_input], 
            outputs=[user_input]
        )
        
        start_btn.click(
            on_start_discussion,
            inputs=[topic_input],
            outputs=[chat_history, topic_input]
        )
        
        stop_btn.click(
            on_stop_discussion,
            inputs=[],
            outputs=[]
        )
        
        # Create a timer for updating the chat and debug output
        timer = gr.HTML("<div id='timer'></div>")
        
        # Set up an interval-based update mechanism
        demo.load(lambda: None, None, None)
        
        # Add a refresh button that will be triggered by JavaScript
        refresh_btn = gr.Button("Refresh", visible=False, elem_id="refresh-btn")
        refresh_btn.click(update_chat, None, chat_history)
        
        # Add a debug refresh button
        debug_refresh_btn = gr.Button("Refresh Debug", visible=False, elem_id="debug-refresh-btn")
        debug_refresh_btn.click(get_debug_log, None, debug_output)
        
        # Add JavaScript for automatic refresh
        js_code = """
        function() {
            const refreshBtn = document.getElementById('refresh-btn');
            const debugRefreshBtn = document.getElementById('debug-refresh-btn');
            
            setInterval(() => {
                if (refreshBtn) {
                    refreshBtn.click();
                }
                if (debugRefreshBtn) {
                    debugRefreshBtn.click();
                }
            }, 1000);
            
            // Report any JavaScript errors
            window.onerror = function(message, source, lineno, colno, error) {
                const errorMsg = `JS Error: ${message} at ${source}:${lineno}:${colno}`;
                console.error(errorMsg);
                if (debugRefreshBtn) {
                    const debugOutput = document.querySelector('textarea[label="Debug Output"]');
                    if (debugOutput) {
                        debugOutput.value += errorMsg + '\\n';
                    }
                }
            };
        }
        """

        demo.load(None, None, None, js=js_code)
    
    return demo


def main():
    try:
        logger.info("Starting application")
        demo = create_gradio_interface()
        logger.info("Launching Gradio interface")
        demo.launch()
    except Exception as e:
        logger.critical(f"Fatal error: {str(e)}\n{traceback.format_exc()}")
        print(f"FATAL ERROR: {str(e)}", file=sys.stderr)

if __name__ == "__main__":
    main()