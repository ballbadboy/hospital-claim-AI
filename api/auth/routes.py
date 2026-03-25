"""Auth endpoints -- login, refresh, user management."""

import logging
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from api.auth.models import (
    LoginRequest, TokenResponse, RefreshRequest,
    UserCreateRequest, UserResponse,
)
from api.auth.jwt_handler import (
    create_access_token, create_refresh_token,
    decode_token, hash_password, verify_password, InvalidToken,
)
from api.auth.middleware import get_current_user, require_role, revoke_token, revoke_all_for_user
from api.dependencies import get_db_session
from core.repositories import UserRepository

logger = logging.getLogger(__name__)
limiter = Limiter(key_func=get_remote_address)

auth_router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@auth_router.post("/login", response_model=TokenResponse)
@limiter.limit("5/5minutes")
async def login(request: Request, body: LoginRequest, session=Depends(get_db_session)):
    user_repo = UserRepository(session)
    user = await user_repo.get_by_username(body.username)

    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid credentials")

    if user.locked_until and user.locked_until > datetime.now(timezone.utc):
        raise HTTPException(status.HTTP_423_LOCKED, "Account locked. Try again later.")

    if not verify_password(body.password, user.hashed_password):
        await user_repo.increment_failed_login(user)
        await session.commit()
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid credentials")

    if not user.is_active:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Account disabled")

    await user_repo.reset_failed_login(user)
    await session.commit()

    token_data = {"sub": user.username, "role": user.role, "user_id": user.id}
    return TokenResponse(
        access_token=create_access_token(token_data),
        refresh_token=create_refresh_token(token_data),
    )


@auth_router.post("/refresh", response_model=TokenResponse)
async def refresh_token_endpoint(body: RefreshRequest):
    try:
        payload = decode_token(body.refresh_token)
    except InvalidToken as e:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, str(e))

    if payload.get("type") != "refresh":
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token type")

    token_data = {"sub": payload["sub"], "role": payload["role"], "user_id": payload["user_id"]}
    return TokenResponse(
        access_token=create_access_token(token_data),
        refresh_token=create_refresh_token(token_data),
    )


@auth_router.post("/revoke/{user_id}")
async def revoke_user_tokens(
    user_id: int,
    admin: dict = Depends(require_role("admin")),
):
    revoke_all_for_user(user_id)
    logger.info("Token revocation requested for user_id=%d by %s", user_id, admin["sub"])
    return {"message": f"All tokens for user {user_id} revoked (in-memory, Phase 2 adds Redis persistence)"}


@auth_router.post("/users", response_model=UserResponse)
async def create_user(
    body: UserCreateRequest,
    admin: dict = Depends(require_role("admin")),
    session=Depends(get_db_session),
):
    user_repo = UserRepository(session)
    existing = await user_repo.get_by_username(body.username)
    if existing:
        raise HTTPException(status.HTTP_409_CONFLICT, "Username already exists")

    valid_roles = {"admin", "coder", "department_head", "finance", "readonly"}
    if body.role not in valid_roles:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Invalid role. Must be one of: {valid_roles}")

    user = await user_repo.create_user(
        username=body.username,
        hashed_password=hash_password(body.password),
        role=body.role,
    )
    await session.commit()
    return UserResponse(id=user.id, username=user.username, role=user.role, is_active=user.is_active)
