from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import time
import logging

class HumanInterjection(BaseModel):
    """Represents a human interjection with metadata."""
    message: str
    timestamp: float = Field(default_factory=time.time)
    context: Optional[Dict[str, Any]] = None

class ConversationState(BaseModel):
    messages: List[Dict[str, Any]] = Field(default_factory=list)
    current_speaker: str = ""
    discussion_topic: str = ""
    human_interjections: List[HumanInterjection] = Field(default_factory=list)
    
    def add_human_interjection(self, message: str, context: Optional[Dict[str, Any]] = None) -> 'ConversationState':
        new_interjection = HumanInterjection(message=message, context=context or {})
        self.human_interjections.append(new_interjection)
        
        # Add the human message explicitly
        self.messages.append({
            "role": "user", 
            "content": message, 
            "type": "interjection"
        })
        
        return self

    def add_agent_response(self, response: str) -> None:
        """Add an agent response to the messages."""
        if response:
            self.messages.append({
                "role": "assistant", 
                "content": response, 
                "type": "response"
            })
        
    def get_latest_response(self) -> str:
        """Retrieve the last message from the conversation."""
        # Find the last assistant message
        for msg in reversed(self.messages):
            if msg.get("role") == "assistant":
                return msg.get("content", "")
        return ""