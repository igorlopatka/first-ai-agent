from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "first-ai-agent"
    deployment_env: Literal["local", "pilot", "prod"] = Field(default="local", alias="DEPLOYMENT_ENV")
    service_host: str = Field(default="127.0.0.1", alias="SERVICE_HOST")
    service_port: int = Field(default=8000, alias="SERVICE_PORT")

    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o-mini", alias="OPENAI_MODEL")

    enable_copilot_channel: bool = Field(default=True, alias="ENABLE_COPILOT_CHANNEL")
    enable_telemetry: bool = Field(default=True, alias="ENABLE_TELEMETRY")
    enable_evaluations: bool = Field(default=True, alias="ENABLE_EVALUATIONS")
    enable_onboarding_prompts: bool = Field(default=True, alias="ENABLE_ONBOARDING_PROMPTS")

    copilot_agent_name: str = Field(default="Workplace Guide", alias="COPILOT_AGENT_NAME")
    copilot_agent_description: str = Field(
        default=(
            "Pomagam prostym jezykiem streszczac, wyjasniac, planowac i redagowac "
            "wiadomosci w pracy biurowej."
        ),
        alias="COPILOT_AGENT_DESCRIPTION",
    )
    copilot_app_id: str = Field(default="local-dev-app-id", alias="COPILOT_APP_ID")
    copilot_test_group: str = Field(default="pilot-users", alias="COPILOT_TEST_GROUP")

    phoenix_collector_endpoint: str | None = Field(
        default=None,
        alias="PHOENIX_COLLECTOR_ENDPOINT",
    )
    phoenix_project_name: str = Field(default="first-ai-agent", alias="PHOENIX_PROJECT_NAME")

    langfuse_public_key: str | None = Field(default=None, alias="LANGFUSE_PUBLIC_KEY")
    langfuse_secret_key: str | None = Field(default=None, alias="LANGFUSE_SECRET_KEY")
    langfuse_host: str = Field(default="http://localhost:3000", alias="LANGFUSE_HOST")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
