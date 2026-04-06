from rich.console import Console

from first_ai_agent.agent import run_agent
from first_ai_agent.config import get_settings
from first_ai_agent.observability import setup_observability
from first_ai_agent.schemas import AgentRequest, ChannelMetadata

console = Console()


EVALUATION_CASES = [
    {
        "prompt": "Wyjasnij prostym jezykiem, do czego sluzy Langfuse w stacku agenta AI.",
        "reference": "Langfuse sluzy do tracingu, analizy promptow i obserwacji odpowiedzi aplikacji LLM.",
    },
    {
        "prompt": "Jak Arize Phoenix pomaga debugowac aplikacje LLM?",
        "reference": "Phoenix pomaga analizowac trace, przebieg promptow i jakosc odpowiedzi modelu.",
    },
    {
        "prompt": "Pomoz mi",
        "reference": "Agent powinien zadac jedno pytanie doprecyzowujace i nie zgadywac intencji.",
    },
    {
        "prompt": "Stresc to dla zarzadu prostym jezykiem.",
        "reference": "Odpowiedz powinna byc zwięzla, uporzadkowana i czytelna dla nietechnicznego odbiorcy.",
    },
    {
        "prompt": "Napisz mail z prosba o przesuniecie terminu projektu o tydzien.",
        "reference": "Agent powinien przygotowac prosty szkic wiadomosci i zaproponowac dalsze kroki.",
    },
    {
        "prompt": "Wyjasnij, czym rozni sie tracing od ewaluacji w AI.",
        "reference": "Tracing obserwuje przebieg i dane wykonania, a ewaluacja mierzy jakosc odpowiedzi.",
    },
    {
        "prompt": "Przygotuj plan wdrozenia pilota agenta AI w firmie.",
        "reference": "Odpowiedz powinna miec kroki, ryzyka i sugerowane nastepne dzialania.",
    },
    {
        "prompt": "Co to jest Ragas?",
        "reference": "Ragas to narzedzie do oceny jakosci odpowiedzi systemow RAG i agentow.",
    },
    {
        "prompt": "Zrob z tego krotkie podsumowanie i napisz mail do zespolu.",
        "reference": "Agent powinien uporzadkowac wiele zadan i odpowiedziec krokami.",
    },
    {
        "prompt": "Wytlumacz to tak, jakbym dopiero zaczynal prace z AI.",
        "reference": "Odpowiedz powinna byc przystepna i pozbawiona nadmiaru zargonu.",
    },
]


def main() -> int:
    settings = get_settings()
    if not settings.openai_api_key:
        console.print("[red]OPENAI_API_KEY is required.[/red]")
        return 1

    if not settings.enable_evaluations:
        console.print("[yellow]Evaluations are disabled by configuration.[/yellow]")
        return 0

    setup_observability(settings)

    samples = []
    for case in EVALUATION_CASES:
        response = run_agent(
            AgentRequest(
                user_message=case["prompt"],
                channel_metadata=ChannelMetadata(channel="api"),
            )
        )
        samples.append((case, response))

    try:
        from ragas import SingleTurnSample, evaluate
        from ragas.dataset_schema import EvaluationDataset
        from ragas.metrics import answer_relevancy, faithfulness
    except Exception as exc:
        console.print(f"[yellow]Ragas evaluation could not start:[/yellow] {exc}")
        return 1

    dataset = EvaluationDataset(
        samples=[
            SingleTurnSample(
                user_input=case["prompt"],
                response=response.answer,
                reference=case["reference"],
            )
            for case, response in samples
        ]
    )

    result = evaluate(dataset=dataset, metrics=[answer_relevancy, faithfulness])
    console.print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
