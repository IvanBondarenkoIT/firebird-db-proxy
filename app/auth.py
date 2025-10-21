"""
Bearer Token аутентификация для API
"""

import logging
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.config import settings

logger = logging.getLogger(__name__)

# HTTP Bearer схема для автоматической документации
security = HTTPBearer()


async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    Проверка Bearer Token из заголовка Authorization.

    Args:
        credentials: Credentials из HTTP Bearer схемы

    Returns:
        str: Валидный токен

    Raises:
        HTTPException: 401 если токен невалидный

    Usage:
        @app.get("/protected")
        async def protected_route(token: str = Depends(verify_token)):
            return {"message": "Access granted"}
    """
    token = credentials.credentials
    valid_tokens = settings.get_api_tokens()

    if token not in valid_tokens:
        # Логируем только первые 10 символов токена для безопасности
        logger.warning(f"Invalid token attempt: {token[:10]}... " f"(length: {len(token)})")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    logger.debug(f"Token verified successfully: {token[:10]}...")
    return token


def get_optional_token(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Optional[str]:
    """
    Опциональная проверка токена (для публичных endpoint'ов).

    Args:
        credentials: Credentials из HTTP Bearer схемы

    Returns:
        Optional[str]: Токен если предоставлен и валиден, None если не предоставлен

    Raises:
        HTTPException: 401 если токен предоставлен но невалидный
    """
    if credentials is None:
        return None

    return verify_token(credentials)
