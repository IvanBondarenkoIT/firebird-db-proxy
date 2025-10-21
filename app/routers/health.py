"""
Router для health check
GET /api/health - проверка работоспособности API и БД
"""

import logging
from datetime import datetime
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.auth import verify_token
from app.database import get_database, FirebirdDatabase, clear_cache
from app.models import HealthResponse
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api",
    tags=["health"]
)

# Время запуска приложения
startup_time = datetime.now()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check",
    description="Проверка работоспособности API и подключения к БД. Не требует аутентификации."
)
async def health_check(
    db: FirebirdDatabase = Depends(get_database)
) -> HealthResponse:
    """
    Health check endpoint для мониторинга.
    
    Проверяет:
    - Работоспособность API
    - Подключение к БД
    - Время работы сервера
    
    Возвращает 200 если все работает, 503 если есть проблемы с БД.
    """
    # Проверка подключения к БД
    db_connected = False
    try:
        db_connected = db.test_connection()
    except Exception as e:
        logger.error(f"Health check: database connection failed - {e}")
    
    # Время работы
    uptime = (datetime.now() - startup_time).total_seconds()
    
    # Статус
    status_str = "healthy" if db_connected else "unhealthy"
    
    response = HealthResponse(
        status=status_str,
        database_connected=db_connected,
        uptime_seconds=uptime,
        version=settings.app_version,
        timestamp=datetime.now()
    )
    
    # Если БД недоступна, возвращаем 503
    if not db_connected:
        logger.warning("Health check: UNHEALTHY (database disconnected)")
        return JSONResponse(
            status_code=503,
            content=response.model_dump(mode='json')
        )
    
    logger.debug(f"Health check: HEALTHY (uptime: {uptime:.0f}s)")
    return response


@router.get(
    "/",
    include_in_schema=False
)
async def root():
    """Корневой endpoint - информация об API"""
    return {
        "message": "Firebird DB Proxy API",
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/api/health"
    }


@router.post(
    "/cache/clear",
    summary="Очистить кеш",
    description="Очищает весь кеш запросов. Требует Bearer Token аутентификацию."
)
async def clear_query_cache(
    token: str = Depends(verify_token)
):
    """Очистить кеш всех запросов"""
    clear_cache()
    return {
        "success": True,
        "message": "Cache cleared successfully",
        "timestamp": datetime.now().isoformat()
    }

