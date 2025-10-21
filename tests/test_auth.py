"""
Тесты аутентификации
"""

import pytest
from fastapi import HTTPException
from app.auth import verify_token
from fastapi.security import HTTPAuthorizationCredentials


class TestAuthentication:
    """Тесты Bearer Token аутентификации"""

    @pytest.mark.asyncio
    async def test_valid_token_accepted(self):
        """Валидный токен должен приниматься"""
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="test-token-1")

        token = await verify_token(credentials)
        assert token == "test-token-1"

    @pytest.mark.asyncio
    async def test_second_valid_token_accepted(self):
        """Второй валидный токен также должен приниматься"""
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="test-token-2")

        token = await verify_token(credentials)
        assert token == "test-token-2"

    @pytest.mark.asyncio
    async def test_invalid_token_rejected(self):
        """Невалидный токен должен отклоняться"""
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="invalid-token")

        with pytest.raises(HTTPException) as exc_info:
            await verify_token(credentials)

        assert exc_info.value.status_code == 401
        assert "Invalid authentication token" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_empty_token_rejected(self):
        """Пустой токен должен отклоняться"""
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="")

        with pytest.raises(HTTPException) as exc_info:
            await verify_token(credentials)

        assert exc_info.value.status_code == 401
