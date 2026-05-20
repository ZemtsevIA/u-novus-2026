from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Skill Assessment Bot"
    debug: bool

    BOT_TOKEN: str
    DATABASE_URL: str

    NEURAL_API_BASE_URL: str
    NEURAL_API_SSL_VERIFY: bool 
    NEURAL_SURVEY_API_ENABLED: bool 
    NEURAL_SURVEY_USE_LLM: bool 
    NEURAL_ASSESSMENT_API_ENABLED: bool 
    NEURAL_API_ERROR_LOG_PATH: str 
    USE_MOCK_NEURAL_API: bool

    MINI_APP_URL: str
    WEBHOOK_URL: str
    RUN_POLLING: bool = True

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
