"""JWT token creation, validation, and password hashing."""

import jwt
import bcrypt
from datetime import datetime, timedelta, timezone

from core.config import get_settings


class InvalidToken(Exception):
    pass


def _get_secret() -> str:
    settings = get_settings()
    if not settings.jwt_secret_key or len(settings.jwt_secret_key) < 32:
        raise InvalidToken("jwt_secret_key must be at least 32 characters")
    return settings.jwt_secret_key


def create_access_token(data: dict) -> str:
    settings = get_settings()
    secret = _get_secret()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_access_token_minutes)
    payload = {**data, "exp": expire, "type": "access"}
    return jwt.encode(payload, secret, algorithm=settings.jwt_algorithm)


def create_refresh_token(data: dict) -> str:
    settings = get_settings()
    secret = _get_secret()
    expire = datetime.now(timezone.utc) + timedelta(hours=settings.jwt_refresh_token_hours)
    payload = {**data, "exp": expire, "type": "refresh"}
    return jwt.encode(payload, secret, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict:
    settings = get_settings()
    secret = _get_secret()
    try:
        payload = jwt.decode(token, secret, algorithms=[settings.jwt_algorithm])
        return payload
    except jwt.ExpiredSignatureError:
        raise InvalidToken("Token has expired")
    except jwt.InvalidTokenError:
        raise InvalidToken("Invalid token")


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
