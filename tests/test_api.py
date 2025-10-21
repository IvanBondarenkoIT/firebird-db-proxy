"""
Интеграционные тесты API endpoints
"""

import pytest


class TestHealthEndpoint:
    """Тесты /api/health endpoint"""
    
    def test_health_check_no_auth(self, client):
        """Health check должен работать без аутентификации"""
        response = client.get("/api/health")
        assert response.status_code in [200, 503]  # 503 если БД недоступна
        
        data = response.json()
        assert "status" in data
        assert "database_connected" in data
        assert "version" in data
        assert "timestamp" in data
    
    def test_health_check_structure(self, client):
        """Health check должен возвращать правильную структуру"""
        response = client.get("/api/health")
        data = response.json()
        
        assert data["status"] in ["healthy", "unhealthy"]
        assert isinstance(data["database_connected"], bool)
        assert isinstance(data["version"], str)
        assert "uptime_seconds" in data


class TestQueryEndpoint:
    """Тесты /api/query endpoint"""
    
    def test_query_without_auth(self, client):
        """Запрос без токена должен возвращать 401"""
        response = client.post(
            "/api/query",
            json={"query": "SELECT 1 FROM RDB$DATABASE"}
        )
        assert response.status_code == 403  # FastAPI returns 403 for missing auth
    
    def test_query_with_invalid_auth(self, client, invalid_auth_headers):
        """Запрос с невалидным токеном должен возвращать 401"""
        response = client.post(
            "/api/query",
            json={"query": "SELECT 1 FROM RDB$DATABASE"},
            headers=invalid_auth_headers
        )
        assert response.status_code == 401
    
    def test_query_with_valid_auth_invalid_sql(self, client, auth_headers):
        """Запрос с валидным токеном но невалидным SQL должен возвращать ошибку"""
        response = client.post(
            "/api/query",
            json={"query": "UPDATE STORGRP SET NAME = 'Test'"},
            headers=auth_headers
        )
        
        # Должен вернуть 200 но с success=false
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "error" in data
        assert "Forbidden" in data["error"] or "validation" in data["error"].lower()
    
    def test_query_empty_body(self, client, auth_headers):
        """Запрос без body должен возвращать 422"""
        response = client.post(
            "/api/query",
            headers=auth_headers
        )
        assert response.status_code == 422
    
    def test_query_invalid_json(self, client, auth_headers):
        """Запрос с невалидным JSON должен возвращать ошибку"""
        response = client.post(
            "/api/query",
            data="invalid json",
            headers=auth_headers
        )
        assert response.status_code == 422
    
    def test_query_missing_query_field(self, client, auth_headers):
        """Запрос без поля query должен возвращать 422"""
        response = client.post(
            "/api/query",
            json={"params": []},
            headers=auth_headers
        )
        assert response.status_code == 422


class TestInfoEndpoints:
    """Тесты /api/tables и /api/schema endpoints"""
    
    def test_tables_without_auth(self, client):
        """Запрос таблиц без токена должен возвращать 401/403"""
        response = client.get("/api/tables")
        assert response.status_code in [401, 403]
    
    def test_tables_with_invalid_auth(self, client, invalid_auth_headers):
        """Запрос таблиц с невалидным токеном должен возвращать 401"""
        response = client.get(
            "/api/tables",
            headers=invalid_auth_headers
        )
        assert response.status_code == 401
    
    def test_schema_without_auth(self, client):
        """Запрос схемы без токена должен возвращать 401/403"""
        response = client.get("/api/schema/STORGRP")
        assert response.status_code in [401, 403]
    
    def test_schema_with_invalid_auth(self, client, invalid_auth_headers):
        """Запрос схемы с невалидным токеном должен возвращать 401"""
        response = client.get(
            "/api/schema/STORGRP",
            headers=invalid_auth_headers
        )
        assert response.status_code == 401


class TestRootEndpoint:
    """Тесты корневого endpoint"""
    
    def test_root_endpoint(self, client):
        """Корневой endpoint должен возвращать информацию об API"""
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "docs" in data
        assert "health" in data


class TestDocumentation:
    """Тесты автоматической документации"""
    
    def test_swagger_ui_available(self, client):
        """Swagger UI должен быть доступен"""
        response = client.get("/docs")
        assert response.status_code == 200
    
    def test_redoc_available(self, client):
        """ReDoc должен быть доступен"""
        response = client.get("/redoc")
        assert response.status_code == 200

