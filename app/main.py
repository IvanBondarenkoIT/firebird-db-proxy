"""
Firebird Database Proxy API - главный модуль приложения

FastAPI приложение для безопасного доступа к Firebird БД через REST API.
"""

import logging
from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.database import initialize_db_pool
from app.routers import query, health, info

# ==================== LOGGING ====================

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='[%(asctime)s] [%(levelname)s] [%(name)s:%(lineno)d] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)

# ==================== RATE LIMITER ====================

limiter = Limiter(key_func=get_remote_address)

# ==================== LIFESPAN ====================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager для инициализации и очистки ресурсов.
    """
    # Startup
    logger.info("=" * 60)
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Environment: {settings.app_env}")
    logger.info(f"Log level: {settings.log_level}")
    logger.info("=" * 60)
    
    # Инициализация БД
    try:
        db_pool = initialize_db_pool()
        logger.info(f"Database: {settings.db_dsn}")
        
        # Тест подключения
        if db_pool.test_connection():
            logger.info("Database connection test: SUCCESS ✓")
        else:
            logger.warning("Database connection test: FAILED ✗")
            logger.warning("API will start but database operations may fail")
    except Exception as e:
        logger.error(f"Failed to initialize database pool: {e}")
        logger.warning("API will start but database operations will fail")
    
    logger.info(f"API server starting on port {settings.port}")
    logger.info("=" * 60)
    
    yield
    
    # Shutdown
    logger.info("=" * 60)
    logger.info("Shutting down gracefully...")
    logger.info(f"{settings.app_name} stopped")
    logger.info("=" * 60)


# ==================== APP INITIALIZATION ====================

app = FastAPI(
    title=settings.app_name,
    description="""
    🔄 **Firebird Database Proxy API**
    
    Безопасный REST API gateway для доступа к Firebird БД с множества устройств.
    
    ## Возможности
    
    * 🔒 **Безопасность**: Bearer Token аутентификация
    * ✅ **Валидация**: Только SELECT запросы разрешены
    * 🚀 **Производительность**: Connection pooling
    * 📊 **Мониторинг**: Health check endpoint
    * 🛡️ **Защита**: Rate limiting от перегрузки
    
    ## Аутентификация
    
    Все защищенные endpoint'ы требуют Bearer Token в заголовке:
    
    ```
    Authorization: Bearer YOUR_TOKEN
    ```
    
    ## Примеры использования
    
    ### Python
    ```python
    import requests
    
    headers = {"Authorization": "Bearer YOUR_TOKEN"}
    response = requests.post(
        "https://api.example.com/api/query",
        json={"query": "SELECT * FROM STORGRP"},
        headers=headers
    )
    print(response.json())
    ```
    
    ### cURL
    ```bash
    curl -X POST https://api.example.com/api/query \\
      -H "Authorization: Bearer YOUR_TOKEN" \\
      -H "Content-Type: application/json" \\
      -d '{"query": "SELECT * FROM STORGRP"}'
    ```
    """,
    version=settings.app_version,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# ==================== MIDDLEWARE ====================

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Rate Limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Логирование всех входящих запросов"""
    start_time = datetime.now()
    
    # Получить IP клиента
    client_ip = request.client.host if request.client else "unknown"
    
    # Получить токен если есть (только первые 10 символов)
    auth_header = request.headers.get("Authorization", "")
    token_preview = ""
    if auth_header.startswith("Bearer "):
        token = auth_header[7:]
        token_preview = f" | Token: {token[:10]}..." if token else ""
    
    logger.info(
        f"→ {request.method} {request.url.path} | IP: {client_ip}{token_preview}"
    )
    
    # Выполнить запрос
    try:
        response = await call_next(request)
        
        # Вычислить время выполнения
        elapsed = (datetime.now() - start_time).total_seconds()
        
        logger.info(
            f"← {request.method} {request.url.path} | "
            f"Status: {response.status_code} | Time: {elapsed:.3f}s"
        )
        
        return response
        
    except Exception as e:
        elapsed = (datetime.now() - start_time).total_seconds()
        logger.error(
            f"✗ {request.method} {request.url.path} | "
            f"Error: {str(e)} | Time: {elapsed:.3f}s"
        )
        raise


# ==================== ROUTERS ====================

# Health check (без rate limiting)
app.include_router(health.router)

# Query endpoint (с rate limiting)
app.include_router(query.router)

# Info endpoints (с rate limiting)
app.include_router(info.router)

# ==================== ERROR HANDLERS ====================

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc: Exception):
    """Обработчик внутренних ошибок"""
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "timestamp": datetime.now().isoformat()
        }
    )


# ==================== MAIN ====================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=settings.app_env == "development",
        log_level=settings.log_level.lower()
    )

