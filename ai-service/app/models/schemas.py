from pydantic import BaseModel, Field


class AgentChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    session_id: str | None = None


class AgentChatResponse(BaseModel):
    reply: str
    session_id: str
    provider: str
