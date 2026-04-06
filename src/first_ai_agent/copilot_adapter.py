from first_ai_agent.agent import run_agent
from first_ai_agent.config import get_settings
from first_ai_agent.observability import build_trace_attributes
from first_ai_agent.schemas import (
    AgentRequest,
    AgentResponse,
    ChannelMetadata,
    CopilotMessage,
    CopilotResponse,
)


ONBOARDING_PROMPTS = [
    "Stresc ten tekst w 5 punktach.",
    "Wyjasnij to prostym jezykiem.",
    "Napisz szkic maila do klienta.",
    "Przygotuj plan dzialania krok po kroku.",
    "Wypisz ryzyka i rekomendacje.",
]


def build_onboarding_payload() -> dict[str, object]:
    settings = get_settings()
    payload: dict[str, object] = {
        "agent_name": settings.copilot_agent_name,
        "agent_description": settings.copilot_agent_description,
    }
    if settings.enable_onboarding_prompts:
        payload["starter_prompts"] = ONBOARDING_PROMPTS
        payload["welcome_message"] = (
            "Pomagam prostym jezykiem streszczac, wyjasniac, planowac i redagowac tresci do pracy."
        )
    return payload


def handle_copilot_message(message: CopilotMessage) -> CopilotResponse:
    settings = get_settings()
    if not settings.enable_copilot_channel:
        response = AgentResponse(
            answer="Ten kanal jest obecnie wylaczony.",
            error_message="Dostep do integracji z Microsoft 365 Copilot nie jest teraz aktywny.",
            intent="general_help",
        )
        return _to_copilot_response(response, message)

    request = AgentRequest(
        user_message=message.text,
        channel_metadata=ChannelMetadata(
            channel="m365_copilot",
            locale=message.locale,
            session_id=message.session_id,
            tenant_id=message.tenant_id,
            user_id=message.user_id,
        ),
        conversation_context=message.conversation_context,
    )
    response = run_agent(request)
    return _to_copilot_response(response, message)


def _to_copilot_response(response: AgentResponse, message: CopilotMessage) -> CopilotResponse:
    parts = [response.answer]
    if response.clarifying_question:
        parts.append(f"Pytanie doprecyzowujące: {response.clarifying_question}")
    if response.error_message:
        parts.append(f"Uwaga: {response.error_message}")

    metadata = build_trace_attributes(
        AgentRequest(
            user_message=message.text,
            channel_metadata=ChannelMetadata(
                channel="m365_copilot",
                locale=message.locale,
                session_id=message.session_id,
                tenant_id=message.tenant_id,
                user_id=message.user_id,
            ),
            conversation_context=message.conversation_context,
        ),
        response=response,
        error_type="user_facing_error" if response.error_message else None,
    )

    return CopilotResponse(
        text="\n\n".join(part for part in parts if part),
        suggested_prompts=response.follow_up_suggestions,
        requires_clarification=bool(response.clarifying_question),
        metadata=metadata,
    )
