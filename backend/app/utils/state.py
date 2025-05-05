from typing import Optional
from pydantic import BaseModel

class AgentState(BaseModel):
    user_message: str
    agent_response: Optional[str] = None
    action_taken: Optional[str] = None
