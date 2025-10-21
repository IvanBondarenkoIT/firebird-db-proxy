"""
Router для получения информации о БД
GET /api/tables - список таблиц
GET /api/schema/{table_name} - схема таблицы
"""

import logging
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Path
import fdb

from app.auth import verify_token
from app.database import get_db_pool, FirebirdConnectionPool
from app.models import TablesResponse, SchemaResponse, ColumnInfo, ErrorResponse

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api",
    tags=["info"]
)


@router.get(
    "/tables",
    response_model=TablesResponse,
    responses={
        401: {"description": "Unauthorized - invalid token"},
        500: {"model": ErrorResponse, "description": "Database error"}
    },
    summary="Получить список таблиц",
    description="Возвращает список всех пользовательских таблиц в БД. Требует Bearer Token аутентификацию."
)
async def get_tables(
    token: str = Depends(verify_token),
    db: FirebirdConnectionPool = Depends(get_db_pool)
) -> TablesResponse:
    """
    Получить список таблиц в БД.
    
    Возвращает только пользовательские таблицы (не системные).
    """
    try:
        logger.info(f"Getting tables list (token: {token[:10]}...)")
        
        tables = db.get_tables()
        
        logger.info(f"Tables list retrieved: {len(tables)} tables")
        
        return TablesResponse(
            success=True,
            tables=tables,
            count=len(tables),
            timestamp=datetime.now()
        )
        
    except fdb.Error as e:
        error_msg = str(e)
        logger.error(f"Database error getting tables: {error_msg}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {error_msg}"
        )
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Unexpected error getting tables: {error_msg}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal error: {error_msg}"
        )


@router.get(
    "/schema/{table_name}",
    response_model=SchemaResponse,
    responses={
        401: {"description": "Unauthorized - invalid token"},
        404: {"model": ErrorResponse, "description": "Table not found"},
        500: {"model": ErrorResponse, "description": "Database error"}
    },
    summary="Получить схему таблицы",
    description="Возвращает список колонок и их типы для указанной таблицы. Требует Bearer Token аутентификацию."
)
async def get_table_schema(
    table_name: str = Path(..., description="Имя таблицы"),
    token: str = Depends(verify_token),
    db: FirebirdConnectionPool = Depends(get_db_pool)
) -> SchemaResponse:
    """
    Получить схему таблицы.
    
    - **table_name**: Имя таблицы (регистр не важен)
    
    Возвращает список колонок с типами данных и информацией о NULL.
    """
    try:
        logger.info(f"Getting schema for table {table_name} (token: {token[:10]}...)")
        
        # Проверить что таблица существует
        all_tables = db.get_tables()
        if table_name.upper() not in [t.upper() for t in all_tables]:
            logger.warning(f"Table not found: {table_name}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Table '{table_name}' not found"
            )
        
        schema = db.get_table_schema(table_name)
        
        # Преобразовать в Pydantic модели
        columns = [
            ColumnInfo(
                name=col['name'],
                type=col['type'],
                nullable=col['nullable']
            )
            for col in schema
        ]
        
        logger.info(f"Schema retrieved for {table_name}: {len(columns)} columns")
        
        return SchemaResponse(
            success=True,
            table=table_name.upper(),
            columns=columns,
            timestamp=datetime.now()
        )
        
    except HTTPException:
        # Re-raise HTTPException как есть
        raise
        
    except fdb.Error as e:
        error_msg = str(e)
        logger.error(f"Database error getting schema for {table_name}: {error_msg}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {error_msg}"
        )
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Unexpected error getting schema for {table_name}: {error_msg}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal error: {error_msg}"
        )

