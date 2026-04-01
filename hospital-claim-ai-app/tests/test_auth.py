import pytest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException


class TestJWTHandler:
    def test_create_access_token(self):
        from api.auth.jwt_handler import create_access_token
        with patch("api.auth.jwt_handler.get_settings") as mock:
            mock.return_value = MagicMock(
                jwt_secret_key="a" * 32, jwt_algorithm="HS256", jwt_access_token_minutes=15,
            )
            token = create_access_token({"sub": "testuser", "role": "coder"})
            assert isinstance(token, str) and len(token) > 0

    def test_decode_access_token(self):
        from api.auth.jwt_handler import create_access_token, decode_token
        with patch("api.auth.jwt_handler.get_settings") as mock:
            mock.return_value = MagicMock(
                jwt_secret_key="a" * 32, jwt_algorithm="HS256", jwt_access_token_minutes=15,
            )
            token = create_access_token({"sub": "testuser", "role": "coder"})
            payload = decode_token(token)
            assert payload["sub"] == "testuser"
            assert payload["role"] == "coder"

    def test_decode_invalid_token_raises(self):
        from api.auth.jwt_handler import decode_token, InvalidToken
        with patch("api.auth.jwt_handler.get_settings") as mock:
            mock.return_value = MagicMock(jwt_secret_key="a" * 32, jwt_algorithm="HS256")
            with pytest.raises(InvalidToken):
                decode_token("invalid.token.here")

    def test_password_hashing(self):
        from api.auth.jwt_handler import hash_password, verify_password
        hashed = hash_password("testpass123")
        assert verify_password("testpass123", hashed) is True
        assert verify_password("wrongpass", hashed) is False

    def test_refuse_empty_secret(self):
        from api.auth.jwt_handler import create_access_token, InvalidToken
        with patch("api.auth.jwt_handler.get_settings") as mock:
            mock.return_value = MagicMock(jwt_secret_key="", jwt_algorithm="HS256", jwt_access_token_minutes=15)
            with pytest.raises(InvalidToken, match="secret_key"):
                create_access_token({"sub": "test"})

    def test_refuse_short_secret(self):
        from api.auth.jwt_handler import create_access_token, InvalidToken
        with patch("api.auth.jwt_handler.get_settings") as mock:
            mock.return_value = MagicMock(jwt_secret_key="short", jwt_algorithm="HS256", jwt_access_token_minutes=15)
            with pytest.raises(InvalidToken, match="secret_key"):
                create_access_token({"sub": "test"})


class TestAuthMiddleware:
    def _make_token(self, data: dict, token_type: str = "access"):
        from api.auth.jwt_handler import create_access_token, create_refresh_token
        with patch("api.auth.jwt_handler.get_settings") as mock:
            mock.return_value = MagicMock(
                jwt_secret_key="a" * 32, jwt_algorithm="HS256",
                jwt_access_token_minutes=15, jwt_refresh_token_hours=8,
            )
            if token_type == "access":
                return create_access_token(data)
            return create_refresh_token(data)

    @pytest.mark.asyncio
    async def test_get_current_user_valid_token(self):
        from api.auth.middleware import get_current_user
        token = self._make_token({"sub": "testuser", "role": "coder"})
        creds = MagicMock()
        creds.credentials = token
        with patch("api.auth.middleware.decode_token") as mock_decode:
            mock_decode.return_value = {"sub": "testuser", "role": "coder", "type": "access"}
            user = await get_current_user(creds)
            assert user["sub"] == "testuser"

    @pytest.mark.asyncio
    async def test_get_current_user_revoked_token(self):
        from api.auth.middleware import get_current_user, revoke_token
        token = self._make_token({"sub": "testuser", "role": "coder"})
        revoke_token(token)
        creds = MagicMock()
        creds.credentials = token
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(creds)
        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_get_current_user_refresh_token_rejected(self):
        from api.auth.middleware import get_current_user
        creds = MagicMock()
        creds.credentials = "some_token"
        with patch("api.auth.middleware.decode_token") as mock_decode:
            mock_decode.return_value = {"sub": "test", "role": "coder", "type": "refresh"}
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(creds)
            assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_require_role_insufficient(self):
        from api.auth.middleware import require_role
        checker = require_role("admin")
        with pytest.raises(HTTPException) as exc_info:
            await checker({"sub": "test", "role": "coder"})
        assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_require_role_sufficient(self):
        from api.auth.middleware import require_role
        checker = require_role("coder", "admin")
        user = await checker({"sub": "test", "role": "coder"})
        assert user["role"] == "coder"
