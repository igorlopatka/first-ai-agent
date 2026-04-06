import os
from collections.abc import Callable

from rich.console import Console

from first_ai_agent.config import Settings
from first_ai_agent.schemas import AgentRequest, AgentResponse

console = Console()


def setup_observability(settings: Settings) -> None:
    if not settings.enable_telemetry:
        console.print("[yellow]Telemetry disabled by configuration.[/yellow]")
        return

    _setup_phoenix(settings)
    _setup_langfuse(settings)


def build_trace_attributes(
    request: AgentRequest,
    response: AgentResponse | None = None,
    error_type: str | None = None,
) -> dict[str, str]:
    attributes = {
        "app.environment": request.channel_metadata.channel,
        "app.channel": request.channel_metadata.channel,
        "app.user_id": request.channel_metadata.user_id or "anonymous",
        "app.session_id": request.channel_metadata.session_id or "unknown",
        "app.locale": request.channel_metadata.locale,
        "app.intent": response.intent if response else detect_intent(request.user_message),
        "app.accessibility_mode": "plain_language",
        "app.has_clarifying_question": str(bool(response and response.clarifying_question)).lower(),
        "app.error_type": error_type or "",
    }
    return attributes


def detect_intent(text: str) -> str:
    lowered = text.lower()
    if any(word in lowered for word in ("streszcz", "podsum", "summary")):
        return "summarization"
    if any(word in lowered for word in ("napisz", "draft", "mail", "email", "wiadomosc")):
        return "drafting"
    if any(word in lowered for word in ("wyjasnij", "explain", "co to", "jak dziala")):
        return "explanation"
    if any(word in lowered for word in ("plan", "kroki", "roadmap", "checklist")):
        return "planning"
    return "general_help"


def _setup_phoenix(settings: Settings) -> None:
    if not settings.phoenix_collector_endpoint:
        return

    os.environ.setdefault("OTEL_EXPORTER_OTLP_TRACES_ENDPOINT", settings.phoenix_collector_endpoint)
    os.environ.setdefault("OTEL_SERVICE_NAME", settings.app_name)
    os.environ.setdefault("PHOENIX_PROJECT_NAME", settings.phoenix_project_name)

    _safe_call("Phoenix tracing", _instrument_phoenix, settings)


def _setup_langfuse(settings: Settings) -> None:
    if not settings.langfuse_public_key or not settings.langfuse_secret_key:
        return

    os.environ.setdefault("LANGFUSE_PUBLIC_KEY", settings.langfuse_public_key)
    os.environ.setdefault("LANGFUSE_SECRET_KEY", settings.langfuse_secret_key)
    os.environ.setdefault("LANGFUSE_HOST", settings.langfuse_host)

    _safe_call("Langfuse tracing", _instrument_langfuse, settings)


def _safe_call(label: str, fn: Callable[[Settings], None], settings: Settings) -> None:
    try:
        fn(settings)
        console.print(f"[green]{label} enabled.[/green]")
    except Exception as exc:  # pragma: no cover
        console.print(f"[yellow]{label} skipped:[/yellow] {exc}")


def _instrument_phoenix(_: Settings) -> None:
    from openinference.instrumentation.agno import AgnoInstrumentor
    from openinference.instrumentation.openai import OpenAIInstrumentor

    OpenAIInstrumentor().instrument()
    AgnoInstrumentor().instrument()


def _instrument_langfuse(settings: Settings) -> None:
    from langfuse import Langfuse

    client = Langfuse(
        public_key=settings.langfuse_public_key,
        secret_key=settings.langfuse_secret_key,
        host=settings.langfuse_host,
    )
    client.auth_check()
