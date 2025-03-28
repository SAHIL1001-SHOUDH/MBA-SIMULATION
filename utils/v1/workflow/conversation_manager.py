from core.v1.graph.discussion_flow import build_conversation_graph
from models.v1.validations.conversation_state import ConversationState

class ConversationManager:
    def __init__(self, topic: str):
        self.topic = topic
        self.graph = build_conversation_graph()
        self.current_state = ConversationState(discussion_topic=topic)
        self.conversation_generator = None
        self.latest_agent_response = ""  # Add a dedicated field to track the latest response

    def start_conversation(self):
        if self.conversation_generator is None:
            self.conversation_generator = self._conversation_stream()
        return next(self.conversation_generator)

    def _conversation_stream(self):
        conversation_history = []
        while not self.is_conversation_complete():
            print("Before invoking graph:", self.current_state.messages)  # Debug print
            
            # Invoke the graph and get the next state
            self.current_state = self.graph.invoke(self.current_state)
            print("After invoking graph:", self.current_state.messages)  # Debug print
            
            # Get the latest response
            latest_response = self.current_state.get_latest_response()
            
            if latest_response:
                print('Response found:', latest_response)
                conversation_history.append(f"Agent: {latest_response}")
                self.latest_agent_response = latest_response  # Store the latest response
                print("Conversation history:", conversation_history)
            
            yield "\n".join(conversation_history)
        
        yield "Conversation Ended."

    def handle_human_interjection(self, message: str) -> str:
        # Add the human interjection to the state
        self.current_state = self.current_state.add_human_interjection(message)
        
        # Invoke the graph with the updated state
        self.current_state = self.graph.invoke(self.current_state)
        
        # Get and store the latest response
        latest_response = self.current_state.get_latest_response()
        self.latest_agent_response = latest_response
        
        return latest_response or "No response generated"

    def is_conversation_complete(self) -> bool:
        return len(self.current_state.messages) > 5