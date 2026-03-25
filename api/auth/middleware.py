"""FastAPI auth dependencies -- require_role, get_current_user."""

import logging
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from api.auth.jwt_handler import decode_token, InvalidToken

logger = logging.getLogger(__name__)
security = HTTPBearer()

_revoked_tokens: set[str] = set()
_revoked_user_ids: set[int] = set()


def revoke_token(token: str) -> None:
    _revoked_tokens.add(token)


def revoke_all_for_user(user_id: int) -> None:
    _revoked_user_ids.add(user_id)


def is_token_revoked(token: str) -> bool:
    return token in _revoked_tokens


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    token = credentials.credentials
    if is_token_revoked(token):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token has been revoked")
    try:
        payload = decode_token(token)
    except InvalidToken as e:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, str(e))
    if payload.get("type") != "access":
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token type")
    if payload.get("user_id") in _revoked_user_ids:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User tokens have been revoked")
    return payload


def require_role(*roles: str):
    async def _check(user: dict = Depends(get_current_user)) -> dict:
        if user.get("role") not in roles:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Insufficient permissions")
        return user
    return _check
