from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Skill Assessment Bot"
    debug: bool = True

    bot_token: str = "123456:change_me"
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/skill_bot"

    neural_api_base_url: str = "https://example.com/api"
    neural_api_token: str = "change_me"
    neural_api_ssl_verify: bool = False
    neural_survey_api_enabled: bool = True
    neural_survey_use_llm: bool = False
    neural_assessment_api_enabled: bool = False
    neural_api_error_log_path: str = "logs/neural_api_errors.log"
    use_mock_neural_api: bool = True

    mini_app_url: str = "https://example.com/miniapp"
    webhook_url: str = "https://example.com/telegram/webhook"
    run_polling: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    @field_validator("debug", mode="before")
    @classmethod
    def normalize_debug(cls, value: object) -> object:
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"release", "prod", "production"}:
                return False
            if normalized in {"debug", "dev", "development"}:
                return True
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
