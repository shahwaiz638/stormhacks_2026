from fastapi import APIRouter

from app.agent.context import ContextStore
from app.agent.service import AgentService
from app.models.schemas import AgentChatRequest, AgentChatResponse

router = APIRouter(prefix='/api/v1/agent', tags=['agent'])
service = AgentService(ContextStore())


@router.post('/chat', response_model=AgentChatResponse)
async def chat(request: AgentChatRequest) -> AgentChatResponse:
  result = await service.chat(message=request.message, session_id=request.session_id)
  return AgentChatResponse(**result)
