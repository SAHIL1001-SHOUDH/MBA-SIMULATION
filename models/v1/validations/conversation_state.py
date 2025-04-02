from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import time

class HumanInterjection(BaseModel):
    message: str
    timestamp: float = Field(default_factory=time.time)
    context: Optional[Dict[str, Any]] = None    

class ConversationState(BaseModel):
    messages: List[Dict[str, Any]] = Field(default_factory=list)
    current_speaker: str = "moderator"
    discussion_topic: str = ""
    human_interjections: List[HumanInterjection] = Field(default_factory=list)
    interrupted: bool = False
    
    def add_human_interjection(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        interjection = HumanInterjection(message=message, context=context or {})
        self.human_interjections.append(interjection)
        self.messages.append({
            "role": "human",
            "content": message,
            "type": "interjection"
        })