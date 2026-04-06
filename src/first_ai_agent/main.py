import json
import sys

from rich.console import Console

from first_ai_agent.agent import run_agent
from first_ai_agent.config import get_settings
from first_ai_agent.observability import setup_observability
from first_ai_agent.schemas import AgentRequest, ChannelMetadata

console = Console()


def main() -> int:
    settings = get_settings()

    if not settings.openai_api_key:
        console.print("[red]OPENAI_API_KEY is required.[/red]")
        console.print("Skopiuj `.env.example` do `.env` i ustaw klucz API.")
        return 1

    if len(sys.argv) < 2:
        console.print('[red]Usage:[/red] python -m first_ai_agent.main "Twoja prosba"')
        return 1

    setup_observability(settings)

    prompt = " ".join(sys.argv[1:]).strip()
    response = run_agent(
        AgentRequest(
            user_message=prompt,
            channel_metadata=ChannelMetadata(channel="cli"),
        )
    )
    console.print(json.dumps(response.model_dump(), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
