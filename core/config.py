import logging

from pydantic import field_validator
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

    his_connectors: list[str] = ["csv"]
    hosxp_db_host: str = ""
    hosxp_db_port: int = 3306
    hosxp_db_name: str = "hosxp_pcu"
    hosxp_db_user: str = ""
    hosxp_db_password: str = ""
    ssb_api_url: str = ""
    ssb_api_key: str = ""

    cors_origins: list[str] = ["http://localhost:3000"]

    jwt_secret_key: str = ""
    jwt_algorithm: str = "HS256"
    jwt_access_token_minutes: int = 15
    jwt_refresh_token_hours: int = 8

    @field_validator("jwt_secret_key")
    @classmethod
    def validate_jwt_secret(cls, v: str) -> str:
        # Allow empty in tests/dev — main.py lifespan checks at startup
        if v and len(v) < 32:
            raise ValueError("jwt_secret_key must be at least 32 characters when set")
        return v

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    return Settings()


def setup_logging() -> None:
    settings = get_settings()
    from pythonjsonlogger import jsonlogger

    handler = logging.StreamHandler()
    handler.setFormatter(jsonlogger.JsonFormatter(
        fmt="%(asctime)s %(name)s %(levelname)s %(message)s",
        rename_fields={"asctime": "timestamp", "levelname": "level"},
    ))
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
