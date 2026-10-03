from fastapi import FastAPI

from app.api.routes.agent import router as agent_router
from app.api.routes.health import router as health_router

app = FastAPI(title='stormhacks-ai-service', version='0.1.0')

app.include_router(health_router)
app.include_router(agent_router)
