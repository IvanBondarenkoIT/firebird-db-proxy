"""
Конфигурация приложения с использованием pydantic-settings
"""

from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Настройки приложения из environment variables"""
    
    # ==================== DATABASE ====================
    db_host: str = Field(default="localhost", description="Firebird server host")
    db_port: int = Field(default=3050, description="Firebird server port")
    db_name: str = Field(default="database.fdb", description="Database name/alias")
    db_user: str = Field(default="SYSDBA", description="Database user")
    db_password: str = Field(default="masterkey", description="Database password")
    db_max_connections: int = Field(default=10, description="Max connections in pool")
    db_connection_timeout: int = Field(default=10, description="Connection timeout in seconds")
    db_query_timeout: int = Field(default=30, description="Query timeout in seconds")
    
    # ==================== SECURITY ====================
    api_tokens: str = Field(
        default="default-token-change-me",
        description="API tokens separated by comma"
    )
    allowed_origins: str = Field(
        default="*",
        description="CORS allowed origins separated by comma"
    )
    
    # ==================== RATE LIMITING ====================
    rate_limit_per_minute: int = Field(default=60, description="Requests per minute")
    rate_limit_per_hour: int = Field(default=1000, description="Requests per hour")
    
    # ==================== LOGGING ====================
    log_level: str = Field(default="INFO", description="Logging level")
    
    # ==================== APPLICATION ====================
    app_name: str = Field(default="Firebird DB Proxy", description="Application name")
    app_version: str = Field(default="1.0.0", description="Application version")
    app_env: str = Field(default="development", description="Environment: development, staging, production")
    
    # Railway автоматически устанавливает PORT
    port: int = Field(default=8000, description="Server port")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    def get_api_tokens(self) -> List[str]:
        """Получить список токенов"""
        return [token.strip() for token in self.api_tokens.split(",") if token.strip()]
    
    def get_allowed_origins(self) -> List[str]:
        """Получить список разрешенных origins для CORS"""
        if self.allowed_origins == "*":
            return ["*"]
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]
    
    @property
    def db_dsn(self) -> str:
        """Получить DSN для подключения к Firebird"""
        return f"{self.db_host}/{self.db_port}:{self.db_name}"


# Глобальный экземпляр настроек
settings = Settings()

