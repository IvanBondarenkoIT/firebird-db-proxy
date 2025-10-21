"""
Pytest конфигурация и fixtures для тестов
"""

import pytest
import os
from fastapi.testclient import TestClient

# Установить тестовые environment variables перед импортом app
os.environ["DB_HOST"] = "localhost"
os.environ["DB_PORT"] = "3050"
os.environ["DB_NAME"] = "test.fdb"
os.environ["DB_USER"] = "SYSDBA"
os.environ["DB_PASSWORD"] = "masterkey"
os.environ["API_TOKENS"] = "test-token-1,test-token-2"
os.environ["RATE_LIMIT_PER_MINUTE"] = "1000"  # Большой лимит для тестов
os.environ["LOG_LEVEL"] = "WARNING"  # Меньше логов в тестах

from app.main import app


@pytest.fixture
def client():
    """Тестовый клиент FastAPI"""
    return TestClient(app)


@pytest.fixture
def auth_headers():
    """Headers с валидным токеном для тестов"""
    return {"Authorization": "Bearer test-token-1"}


@pytest.fixture
def invalid_auth_headers():
    """Headers с невалидным токеном"""
    return {"Authorization": "Bearer invalid-token"}
