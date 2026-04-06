import json

from agno.agent import Agent
from agno.models.openai import OpenAIChat

from first_ai_agent.config import get_settings
from first_ai_agent.observability import detect_intent
from first_ai_agent.schemas import AgentRequest, AgentResponse


SYSTEM_INSTRUCTIONS = [
    "Odpowiadaj prostym, przyjaznym jezykiem po polsku, chyba ze uzytkownik wyraznie poprosi inaczej.",
    "Zacznij od krotkiej odpowiedzi, a dopiero potem dodaj zwięzle kroki lub wskazowki.",
    "Jesli prosba jest niejasna, zadaj jedno pytanie doprecyzowujace zamiast zgadywac.",
    "Unikaj zargonu. Gdy uzywasz trudnego terminu, wyjasnij go prostym zdaniem.",
    "Zaproponuj 2-3 sensowne dalsze kroki, kiedy to pomaga uzytkownikowi.",
    "Nie twierdz, ze wykonales akcje w systemach firmowych, jesli nie masz takiej mozliwosci.",
]


def build_agent() -> Agent:
    settings = get_settings()
    return Agent(
        model=OpenAIChat(id=settings.openai_model, api_key=settings.openai_api_key),
        markdown=True,
        description="Przyjazny asystent do pracy biurowej osadzany w Microsoft 365 Copilot.",
        instructions=SYSTEM_INSTRUCTIONS,
    )


def run_agent(request: AgentRequest) -> AgentResponse:
    user_message = request.user_message.strip()

    if not user_message:
        return AgentResponse(
            answer="Potrzebuje chociaz jednego zdania, zeby pomoc.",
            clarifying_question="Napisz prosze, czego potrzebujesz: streszczenia, wyjasnienia, planu czy szkicu wiadomosci?",
            follow_up_suggestions=_default_suggestions("general_help"),
            confidence_note="Im bardziej konkretny opis celu, tym lepsza odpowiedz.",
            intent="general_help",
        )

    if _needs_clarification(user_message):
        intent = detect_intent(user_message)
        return AgentResponse(
            answer="Moge pomoc, ale najpierw potrzebuje odrobiny doprecyzowania.",
            clarifying_question=_build_clarifying_question(user_message),
            follow_up_suggestions=_default_suggestions(intent),
            confidence_note="Na razie nie zgaduje, zeby nie poprowadzic Cie w zla strone.",
            intent=intent,
        )

    if len(user_message) > 3500:
        return AgentResponse(
            answer=(
                "Widze dluzszy material. Najlepiej bedzie najpierw go strescic, a potem przejsc do kolejnych krokow."
            ),
            clarifying_question="Czy chcesz krotkie streszczenie, liste najwazniejszych punktow czy plan dzialania na podstawie tego tekstu?",
            follow_up_suggestions=[
                "Stresc to w 5 punktach.",
                "Wyciagnij najwazniejsze ryzyka i decyzje.",
                "Zamien to na plan dzialania.",
            ],
            confidence_note="Dzielac dlugi material na kroki, latwiej utrzymac czytelnosc i jakosc odpowiedzi.",
            intent="summarization",
        )

    agent = build_agent()
    prompt = _build_structured_prompt(request)

    try:
        result = agent.run(prompt)
        content = getattr(result, "content", str(result))
        return _parse_agent_response(content, request)
    except Exception:
        intent = detect_intent(user_message)
        return AgentResponse(
            answer="Nie udalo mi sie teraz przygotowac odpowiedzi.",
            error_message="Wystapil chwilowy problem techniczny. Sprobuj ponownie za moment albo uprosc prosbe do jednego zadania.",
            follow_up_suggestions=_default_suggestions(intent),
            confidence_note="Problem wyglada na techniczny, nie na blad w Twojej prosbie.",
            intent=intent,
        )


def _build_structured_prompt(request: AgentRequest) -> str:
    history = "\n".join(f"{turn.role}: {turn.content}" for turn in request.conversation_context[-6:])
    return f"""
Odpowiedz jako przyjazny asystent workplace w Microsoft 365 Copilot.

Zadanie uzytkownika:
{request.user_message}

Historia kontekstu:
{history or "brak"}

Zwroc odpowiedz w JSON bez dodatkowego tekstu, uzywajac pol:
- answer: string
- follow_up_suggestions: array[string] (2 lub 3 pozycje)
- clarifying_question: string lub null
- confidence_note: string lub null
- error_message: string lub null

Wymagania:
- prosty jezyk
- krotka odpowiedz na poczatku
- brak zargonu bez wyjasnienia
- jesli prosba obejmuje kilka rzeczy, uporzadkuj odpowiedz krokami
- jesli wciaz czegos brakuje, ustaw clarifying_question
""".strip()


def _parse_agent_response(content: str, request: AgentRequest) -> AgentResponse:
    intent = detect_intent(request.user_message)
    try:
        payload = json.loads(content)
        response = AgentResponse.model_validate(
            {
                "answer": payload.get("answer") or "Przygotowalem odpowiedz, ale nie wszystko dalo sie dobrze sformatowac.",
                "follow_up_suggestions": payload.get("follow_up_suggestions") or _default_suggestions(intent),
                "clarifying_question": payload.get("clarifying_question"),
                "confidence_note": payload.get("confidence_note"),
                "error_message": payload.get("error_message"),
                "intent": intent,
            }
        )
        return response
    except Exception:
        return AgentResponse(
            answer=content.strip() or "Przygotowalem odpowiedz, ale nie udalo sie jej dobrze zinterpretowac.",
            follow_up_suggestions=_default_suggestions(intent),
            confidence_note="Odpowiedz zostala uproszczona, bo model nie zwrocil pelnej struktury.",
            intent=intent,
        )


def _needs_clarification(text: str) -> bool:
    lowered = text.lower().strip()
    vague_phrases = {
        "pomoz mi",
        "help me",
        "co sadzisz",
        "zrob to",
        "ogarnij to",
        "potrzebuje pomocy",
    }
    if lowered in vague_phrases:
        return True
    return len(lowered.split()) < 3


def _build_clarifying_question(text: str) -> str:
    intent = detect_intent(text)
    if intent == "drafting":
        return "Jaki rodzaj wiadomosci mam przygotowac i do kogo ma byc skierowana?"
    if intent == "summarization":
        return "Jak krotkie ma byc streszczenie: 3 punkty, 5 punktow czy jedno krotkie podsumowanie?"
    if intent == "planning":
        return "Jaki cel chcesz osiagnac i na kiedy potrzebujesz plan?"
    if intent == "explanation":
        return "Co mam wyjasnic i na jakim poziomie prostoty: bardzo prosto czy bardziej szczegolowo?"
    return "Czego dokladnie potrzebujesz: wyjasnienia, streszczenia, planu czy szkicu wiadomosci?"


def _default_suggestions(intent: str) -> list[str]:
    if intent == "drafting":
        return [
            "Napisz to krocej i bardziej uprzejmie.",
            "Przeredaguj to na mail do klienta.",
            "Dodaj jasne wezwanie do dzialania.",
        ]
    if intent == "summarization":
        return [
            "Stresc to w 5 punktach.",
            "Wypisz najwazniejsze decyzje.",
            "Wskaz ryzyka i kolejne kroki.",
        ]
    if intent == "planning":
        return [
            "Rozbij to na kroki na najblizszy tydzien.",
            "Zamien to na checklistę.",
            "Wskaz najwazniejsze ryzyka i zaleznosci.",
        ]
    if intent == "explanation":
        return [
            "Wyjasnij to prostszym jezykiem.",
            "Podaj krotki przyklad.",
            "Porownaj to z prostsza alternatywa.",
        ]
    return [
        "Wyjasnij to prostym jezykiem.",
        "Przygotuj plan dzialania krok po kroku.",
        "Stresc to w kilku punktach.",
    ]
