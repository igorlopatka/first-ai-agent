from fastapi import FastAPI
from fastapi.responses import JSONResponse

from first_ai_agent.agent import run_agent
from first_ai_agent.config import get_settings
from first_ai_agent.copilot_adapter import build_onboarding_payload, handle_copilot_message
from first_ai_agent.observability import setup_observability
from first_ai_agent.schemas import AgentRequest, CopilotMessage

settings = get_settings()
setup_observability(settings)

app = FastAPI(
    title="First AI Agent Service",
    version="0.2.0",
    description="Backend service for a Microsoft 365 Copilot-first workplace assistant.",
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "environment": settings.deployment_env}


@app.get("/api/v1/copilot/onboarding")
def copilot_onboarding() -> dict[str, object]:
    return build_onboarding_payload()


@app.post("/api/v1/agent/respond")
def agent_respond(request: AgentRequest) -> JSONResponse:
    response = run_agent(request)
    return JSONResponse(content=response.model_dump())


@app.post("/api/v1/copilot/message")
def copilot_message(message: CopilotMessage) -> JSONResponse:
    response = handle_copilot_message(message)
    return JSONResponse(content=response.model_dump())
