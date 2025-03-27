from langchain_core.messages import BaseMessage
from pydantic import BaseModel
from typing import List, Dict, Any, Optional


class ConversationState(BaseModel):
    messages: List[BaseMessage]
    current_speaker: str
    discussion_topic: str
    pending_user_message: Optional[str] = None
    user_interjection_allowed: bool = True