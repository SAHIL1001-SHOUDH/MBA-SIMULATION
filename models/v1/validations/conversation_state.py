from pydantic import BaseModel
from typing import List, Dict, Any


class ConversationState(BaseModel):
    messages: List[Dict[str, Any]]
    current_speaker: str
    discussion_topic: str
