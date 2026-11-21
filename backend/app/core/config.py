from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Server
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    API_V1_PREFIX: str = "/api/v1"
    SECRET_KEY: str = "costguard-secret-key-change-in-production"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://costguard:costguard_secret@localhost:5432/costguard_db"
    DATABASE_SYNC_URL: str = "postgresql+psycopg2://costguard:costguard_secret@localhost:5432/costguard_db"

    # LLM Providers
    OPENAI_API_KEY: str | None = None
    ANTHROPIC_API_KEY: str | None = None
    GEMINI_API_KEY: str | None = None
    OLLAMA_BASE_URL: str = "http://localhost:11434"

    # Timeouts & Limits
    DEFAULT_TIMEOUT_SECONDS: float = 60.0
    MAX_RETRIES: int = 2


@lru_cache
def get_settings() -> Settings:
    return Settings()
