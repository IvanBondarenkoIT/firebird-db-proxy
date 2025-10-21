"""
Валидация SQL запросов для безопасности
Только SELECT и WITH запросы разрешены
"""

import re
import logging
from typing import Tuple

logger = logging.getLogger(__name__)

# Запрещенные SQL операции (регулярные выражения)
FORBIDDEN_PATTERNS = [
    r'\b(INSERT|UPDATE|DELETE|DROP|ALTER|TRUNCATE|CREATE|GRANT|REVOKE)\b',
    r'\b(EXECUTE\s+BLOCK)\b',
    r'\b(EXECUTE\s+PROCEDURE)\b',
    r';.*;\s*',  # Множественные запросы через точку с запятой
]


def validate_sql(query: str) -> Tuple[bool, str]:
    """
    Валидация SQL запроса на безопасность.
    
    Args:
        query: SQL запрос для валидации
        
    Returns:
        Tuple[bool, str]: (is_valid, error_message)
            - is_valid: True если запрос безопасен, False если нет
            - error_message: Сообщение об ошибке или "OK"
    
    Examples:
        >>> validate_sql("SELECT * FROM STORGRP")
        (True, "OK")
        
        >>> validate_sql("UPDATE STORGRP SET NAME = 'Test'")
        (False, "Forbidden operation detected: UPDATE")
    """
    if not query or not query.strip():
        return False, "Empty query not allowed"
    
    # Удалить SQL комментарии
    # Однострочные комментарии: -- комментарий
    query_clean = re.sub(r'--.*$', '', query, flags=re.MULTILINE)
    # Многострочные комментарии: /* комментарий */
    query_clean = re.sub(r'/\*.*?\*/', '', query_clean, flags=re.DOTALL)
    
    # Проверка на запрещенные паттерны
    for pattern in FORBIDDEN_PATTERNS:
        match = re.search(pattern, query_clean, re.IGNORECASE)
        if match:
            forbidden_op = match.group(0)
            error_msg = f"Forbidden operation detected: {forbidden_op}"
            logger.warning(f"SQL validation failed: {error_msg}")
            logger.debug(f"Blocked query: {query[:100]}...")
            return False, error_msg
    
    # Проверка что это SELECT или WITH запрос
    query_stripped = query_clean.strip().upper()
    if not (query_stripped.startswith('SELECT') or query_stripped.startswith('WITH')):
        error_msg = "Only SELECT and WITH queries are allowed"
        logger.warning(f"SQL validation failed: {error_msg}")
        logger.debug(f"Blocked query: {query[:100]}...")
        return False, error_msg
    
    logger.debug("SQL validation passed")
    return True, "OK"


def sanitize_query(query: str) -> str:
    """
    Очистка запроса от лишних пробелов и переносов строк.
    
    Args:
        query: SQL запрос
        
    Returns:
        str: Очищенный запрос
    """
    # Удалить лишние пробелы
    query = re.sub(r'\s+', ' ', query)
    # Удалить пробелы в начале и конце
    query = query.strip()
    return query

