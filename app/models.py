"""
Pydantic модели для API requests и responses
"""

from typing import Any, Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, validator


# ==================== REQUEST MODELS ====================

class QueryRequest(BaseModel):
    """Запрос на выполнение SQL"""
    
    query: str = Field(
        ...,
        description="SQL запрос (только SELECT или WITH)",
        min_length=1,
        max_length=10000
    )
    params: Optional[List[Any]] = Field(
        default=None,
        description="Параметры запроса (позиционные)"
    )
    
    @validator('query')
    def query_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Query cannot be empty')
        return v.strip()
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "SELECT ID, NAME FROM STORGRP WHERE ID = ?",
                "params": [1]
            }
        }


# ==================== RESPONSE MODELS ====================

class QueryResponse(BaseModel):
    """Ответ на выполнение SQL запроса"""
    
    success: bool = Field(..., description="Успешность выполнения")
    data: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Результаты запроса (массив объектов)"
    )
    rows_count: Optional[int] = Field(
        default=None,
        description="Количество возвращенных строк"
    )
    execution_time: Optional[float] = Field(
        default=None,
        description="Время выполнения запроса в секундах"
    )
    error: Optional[str] = Field(
        default=None,
        description="Сообщение об ошибке"
    )
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="Время ответа"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": [
                    {"ID": 1, "NAME": "Магазин 1"},
                    {"ID": 2, "NAME": "Магазин 2"}
                ],
                "rows_count": 2,
                "execution_time": 0.234,
                "timestamp": "2025-10-21T12:34:56.789Z"
            }
        }


class ErrorResponse(BaseModel):
    """Ответ с ошибкой"""
    
    success: bool = Field(default=False, description="Всегда False")
    error: str = Field(..., description="Сообщение об ошибке")
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="Время ответа"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "error": "SQL validation failed: UPDATE not allowed",
                "timestamp": "2025-10-21T12:34:56.789Z"
            }
        }


class HealthResponse(BaseModel):
    """Ответ health check endpoint"""
    
    status: str = Field(..., description="Статус: healthy или unhealthy")
    database_connected: bool = Field(..., description="Подключение к БД работает")
    uptime_seconds: Optional[float] = Field(
        default=None,
        description="Время работы сервера в секундах"
    )
    version: str = Field(..., description="Версия API")
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="Время ответа"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "database_connected": True,
                "uptime_seconds": 3600,
                "version": "1.0.0",
                "timestamp": "2025-10-21T12:34:56.789Z"
            }
        }


class TablesResponse(BaseModel):
    """Ответ с списком таблиц"""
    
    success: bool = Field(default=True, description="Успешность выполнения")
    tables: List[str] = Field(..., description="Список имен таблиц")
    count: int = Field(..., description="Количество таблиц")
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="Время ответа"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "tables": ["STORGRP", "STORZAKAZDT", "STORZDTGDS", "GOODS"],
                "count": 4,
                "timestamp": "2025-10-21T12:34:56.789Z"
            }
        }


class ColumnInfo(BaseModel):
    """Информация о колонке таблицы"""
    
    name: str = Field(..., description="Имя колонки")
    type: str = Field(..., description="Тип данных")
    nullable: bool = Field(..., description="Допускает NULL")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "ID",
                "type": "INTEGER",
                "nullable": False
            }
        }


class SchemaResponse(BaseModel):
    """Ответ со схемой таблицы"""
    
    success: bool = Field(default=True, description="Успешность выполнения")
    table: str = Field(..., description="Имя таблицы")
    columns: List[ColumnInfo] = Field(..., description="Список колонок")
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="Время ответа"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "table": "STORGRP",
                "columns": [
                    {"name": "ID", "type": "INTEGER", "nullable": False},
                    {"name": "NAME", "type": "VARCHAR", "nullable": True}
                ],
                "timestamp": "2025-10-21T12:34:56.789Z"
            }
        }

