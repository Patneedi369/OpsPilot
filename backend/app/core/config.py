from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "opspilot-api"
    app_env: str = "development"
    api_v1_prefix: str = "/api/v1"
    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "INFO"
    secret_key: str = "opspilot-secure-secret-key-2026-prod"
    jwt_algorithm: str = "HS256"
    ai_timeout_seconds: float = 30.0
    cors_origins: str = (
        "http://localhost:5173,http://127.0.0.1:5173,"
        "http://localhost:5174,http://127.0.0.1:5174,"
        "http://localhost:3000,http://127.0.0.1:3000"
    )
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5433/opspilot"
    redis_url: str = "redis://localhost:6379/0"
    anthropic_api_key: str = ""
    ai_model: str = "claude-sonnet-4-6"
    ai_provider: str = "anthropic"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
