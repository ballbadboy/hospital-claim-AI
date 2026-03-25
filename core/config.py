import logging

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    app_name: str = "Hospital Claim AI"
    app_version: str = "1.0.0"
    app_env: str = "development"
    log_level: str = "INFO"

    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-4-20250514"
    anthropic_max_tokens: int = 4096

    database_url: str = "postgresql+asyncpg://localhost:5432/hospital_claim_ai"

    line_channel_token: str = ""
    line_channel_secret: str = ""

    fdh_api_url: str = "https://fdh.moph.go.th/api"
    fdh_api_key: str = ""

    fast_track_hours: int = 24
    normal_submit_days: int = 30

    cors_origins: list[str] = ["http://localhost:3000"]

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    return Settings()


def setup_logging() -> None:
    settings = get_settings()
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
    )
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
