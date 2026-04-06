from typing import Literal

from pydantic import BaseModel, Field


class ChannelMetadata(BaseModel):
    channel: Literal["cli", "m365_copilot", "api"] = "cli"
    locale: str = "pl-PL"
    session_id: str | None = None
    tenant_id: str | None = None
    user_id: str | None = None
    message_id: str | None = None


class ConversationTurn(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str = Field(..., min_length=1)


class AgentRequest(BaseModel):
    user_message: str = Field(..., min_length=1, description="Wiadomosc uzytkownika.")
    channel_metadata: ChannelMetadata = Field(default_factory=ChannelMetadata)
    conversation_context: list[ConversationTurn] = Field(default_factory=list)


class AgentResponse(BaseModel):
    answer: str = Field(..., description="Glowne streszczenie lub odpowiedz dla uzytkownika.")
    follow_up_suggestions: list[str] = Field(
        default_factory=list,
        description="Krotkie, przyjazne propozycje dalszych krokow.",
    )
    clarifying_question: str | None = Field(
        default=None,
        description="Pytanie doprecyzowujace, gdy intencja nie jest jasna.",
    )
    confidence_note: str | None = Field(
        default=None,
        description="Krotka informacja o ograniczeniach lub poziomie pewnosci odpowiedzi.",
    )
    error_message: str | None = Field(
        default=None,
        description="Czytelny komunikat bledu dla uzytkownika koncowego.",
    )
    intent: str = Field(default="general_help")
    accessibility_mode: Literal["plain_language"] = "plain_language"


class CopilotMessage(BaseModel):
    text: str = Field(..., min_length=1)
    user_id: str = Field(..., min_length=1)
    tenant_id: str | None = None
    session_id: str | None = None
    locale: str = "pl-PL"
    conversation_context: list[ConversationTurn] = Field(default_factory=list)


class CopilotResponse(BaseModel):
    text: str
    suggested_prompts: list[str] = Field(default_factory=list)
    requires_clarification: bool = False
    metadata: dict[str, str] = Field(default_factory=dict)
