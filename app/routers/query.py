"""
Router для выполнения SQL запросов
POST /api/query - выполнение SELECT запросов
"""

import logging
from datetime import datetime
from fastapi import APIRouter, Depends
import fdb

from app.auth import verify_token
from app.database import get_database, FirebirdDatabase
from app.models import QueryRequest, QueryResponse, ErrorResponse
from app.validators import validate_sql

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["query"])


@router.post(
    "/query",
    response_model=QueryResponse,
    responses={
        400: {"model": ErrorResponse, "description": "SQL validation failed"},
        401: {"description": "Unauthorized - invalid token"},
        500: {"model": ErrorResponse, "description": "Database error"},
    },
    summary="Выполнить SQL запрос",
    description="Выполняет SELECT или WITH запрос к Firebird БД. Требует Bearer Token аутентификацию.",
)
async def execute_query(
    request: QueryRequest,
    token: str = Depends(verify_token),
    db: FirebirdDatabase = Depends(get_database),
) -> QueryResponse:
    """
    Выполнение SELECT запроса к БД.

    - **query**: SQL запрос (только SELECT или WITH)
    - **params**: Опциональные параметры запроса

    Возвращает результаты в виде массива объектов.
    """
    start_time = datetime.now()

    # Валидация SQL
    is_valid, error_message = validate_sql(request.query)
    if not is_valid:
        logger.warning(f"SQL validation failed: {error_message}")
        return QueryResponse(
            success=False, error=f"SQL validation failed: {error_message}", timestamp=datetime.now()
        )

    # Выполнение запроса
    try:
        # Преобразовать params из List в Tuple если есть
        params = tuple(request.params) if request.params else None

        logger.info(f"Executing query (token: {token[:10]}...)")
        logger.debug(f"Query: {request.query[:200]}...")

        results = db.execute_query(request.query, params)

        execution_time = (datetime.now() - start_time).total_seconds()

        logger.info(f"Query successful: {len(results)} rows, {execution_time:.3f}s")

        return QueryResponse(
            success=True,
            data=results,
            rows_count=len(results),
            execution_time=execution_time,
            timestamp=datetime.now(),
        )

    except fdb.Error as e:
        execution_time = (datetime.now() - start_time).total_seconds()
        error_msg = str(e)

        logger.error(f"Database error after {execution_time:.3f}s: {error_msg}")

        return QueryResponse(
            success=False,
            error=f"Database error: {error_msg}",
            execution_time=execution_time,
            timestamp=datetime.now(),
        )

    except Exception as e:
        execution_time = (datetime.now() - start_time).total_seconds()
        error_msg = str(e)

        logger.error(f"Unexpected error after {execution_time:.3f}s: {error_msg}")

        return QueryResponse(
            success=False,
            error=f"Internal error: {error_msg}",
            execution_time=execution_time,
            timestamp=datetime.now(),
        )
