"""
Firebird database connection и операции с БД (с кешированием)
"""

import fdb
import logging
import hashlib
import json
from contextlib import contextmanager
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, date, time, timedelta
import decimal

from app.config import settings

logger = logging.getLogger(__name__)

# Простой in-memory кеш для запросов
_query_cache: Dict[str, Dict[str, Any]] = {}
CACHE_TTL_SECONDS = 300  # 5 минут по умолчанию


class FirebirdDatabase:
    """
    Firebird БД с подключением по требованию и кешированием.
    """
    
    def __init__(
        self,
        host: str,
        port: int,
        database: str,
        user: str,
        password: str,
        connection_timeout: int = 10,
        cache_ttl: int = 300
    ):
        """
        Инициализация параметров подключения.
        
        Args:
            host: Хост Firebird сервера
            port: Порт Firebird сервера
            database: Имя БД или alias
            user: Пользователь БД
            password: Пароль пользователя
            connection_timeout: Таймаут подключения в секундах
            cache_ttl: Время жизни кеша в секундах (по умолчанию 5 минут)
        """
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.connection_timeout = connection_timeout
        self.cache_ttl = cache_ttl
        
        self.dsn = f"{host}/{port}:{database}"
        logger.info(f"Initialized Firebird database: {self.dsn}")
        logger.info(f"Cache TTL: {cache_ttl}s")
    
    def _get_cache_key(self, query: str, params: Optional[Tuple] = None) -> str:
        """Генерация ключа кеша для запроса"""
        cache_data = {
            "query": query,
            "params": params if params else []
        }
        cache_string = json.dumps(cache_data, sort_keys=True)
        return hashlib.md5(cache_string.encode()).hexdigest()
    
    def _get_from_cache(self, cache_key: str) -> Optional[List[Dict[str, Any]]]:
        """Получить данные из кеша если актуальны"""
        if cache_key in _query_cache:
            cached = _query_cache[cache_key]
            if datetime.now() < cached['expires_at']:
                logger.debug(f"Cache HIT: {cache_key}")
                return cached['data']
            else:
                # Кеш устарел, удаляем
                logger.debug(f"Cache EXPIRED: {cache_key}")
                del _query_cache[cache_key]
        return None
    
    def _save_to_cache(self, cache_key: str, data: List[Dict[str, Any]]):
        """Сохранить данные в кеш"""
        _query_cache[cache_key] = {
            'data': data,
            'expires_at': datetime.now() + timedelta(seconds=self.cache_ttl)
        }
        logger.debug(f"Cache SAVED: {cache_key} ({len(data)} rows)")
    
    @contextmanager
    def get_connection(self):
        """
        Context manager для получения соединения с автоматической очисткой.
        
        Yields:
            fdb.Connection: Соединение с БД
            
        Raises:
            fdb.Error: Ошибки подключения или работы с БД
            
        Example:
            with db_pool.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM TABLE")
        """
        conn = None
        try:
            logger.debug(f"Connecting to {self.dsn}")
            start_time = datetime.now()
            
            conn = fdb.connect(
                dsn=self.dsn,
                user=self.user,
                password=self.password,
                charset='UTF8'
            )
            
            elapsed = (datetime.now() - start_time).total_seconds()
            logger.debug(f"Connection established in {elapsed:.3f}s")
            
            yield conn
            
        except fdb.Error as e:
            logger.error(f"Database connection error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in database connection: {e}")
            raise
        finally:
            if conn:
                try:
                    conn.close()
                    logger.debug("Connection closed")
                except Exception as e:
                    logger.warning(f"Error closing connection: {e}")
    
    def execute_query(
        self,
        query: str,
        params: Optional[Tuple] = None,
        use_cache: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Выполнение SELECT запроса с кешированием.
        
        Args:
            query: SQL запрос
            params: Параметры запроса (tuple для позиционных параметров)
            use_cache: Использовать ли кеш (по умолчанию True)
            
        Returns:
            List[Dict[str, Any]]: Список строк в виде словарей {column_name: value}
            
        Raises:
            fdb.Error: Ошибки выполнения запроса
        """
        # Проверяем кеш
        cache_key = self._get_cache_key(query, params) if use_cache else None
        if cache_key:
            cached_data = self._get_from_cache(cache_key)
            if cached_data is not None:
                return cached_data
        
        start_time = datetime.now()
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            try:
                # Выполнение запроса
                if params:
                    logger.debug(f"Executing query with {len(params)} parameters")
                    cursor.execute(query, params)
                else:
                    logger.debug("Executing query without parameters")
                    cursor.execute(query)
                
                # Получить названия колонок
                if cursor.description:
                    columns = [desc[0] for desc in cursor.description]
                    
                    # Получить данные
                    rows = cursor.fetchall()
                    
                    # Преобразовать в список словарей
                    results = []
                    for row in rows:
                        row_dict = {}
                        for i, col_name in enumerate(columns):
                            value = row[i]
                            # Преобразовать типы данных для JSON сериализации
                            if isinstance(value, datetime):
                                value = value.isoformat()
                            elif isinstance(value, date):
                                value = value.isoformat()
                            elif isinstance(value, time):
                                value = value.isoformat()
                            elif isinstance(value, decimal.Decimal):
                                value = float(value)
                            elif isinstance(value, bytes):
                                value = value.decode('utf-8', errors='replace')
                            row_dict[col_name] = value
                        results.append(row_dict)
                    
                    elapsed = (datetime.now() - start_time).total_seconds()
                    logger.info(
                        f"Query executed: {len(results)} rows in {elapsed:.3f}s"
                    )
                    
                    # Сохраняем в кеш
                    if cache_key:
                        self._save_to_cache(cache_key, results)
                    
                    return results
                else:
                    # Нет результатов (не должно происходить для SELECT)
                    logger.warning("Query returned no description (no results)")
                    return []
                    
            except fdb.Error as e:
                elapsed = (datetime.now() - start_time).total_seconds()
                logger.error(f"Query execution failed after {elapsed:.3f}s: {e}")
                raise
            finally:
                cursor.close()
    
    def test_connection(self) -> bool:
        """
        Проверка подключения к БД.
        
        Returns:
            bool: True если подключение успешно, False если нет
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1 FROM RDB$DATABASE")
                result = cursor.fetchone()
                cursor.close()
                
                if result and result[0] == 1:
                    logger.info("Database connection test: SUCCESS")
                    return True
                else:
                    logger.error("Database connection test: FAILED (unexpected result)")
                    return False
                    
        except Exception as e:
            logger.error(f"Database connection test: FAILED - {e}")
            return False
    
    def get_tables(self) -> List[str]:
        """
        Получить список пользовательских таблиц в БД.
        
        Returns:
            List[str]: Список имен таблиц
        """
        query = """
            SELECT RDB$RELATION_NAME
            FROM RDB$RELATIONS
            WHERE RDB$SYSTEM_FLAG = 0
                AND RDB$VIEW_BLR IS NULL
            ORDER BY RDB$RELATION_NAME
        """
        
        results = self.execute_query(query)
        tables = [row['RDB$RELATION_NAME'].strip() for row in results]
        
        logger.info(f"Found {len(tables)} tables in database")
        return tables
    
    def get_table_schema(self, table_name: str) -> List[Dict[str, Any]]:
        """
        Получить схему таблицы (список колонок и их типы).
        
        Args:
            table_name: Имя таблицы
            
        Returns:
            List[Dict[str, Any]]: Список колонок с информацией о типах
        """
        query = """
            SELECT
                f.RDB$FIELD_NAME as FIELD_NAME,
                f.RDB$FIELD_TYPE as FIELD_TYPE,
                f.RDB$NULL_FLAG as NULL_FLAG,
                t.RDB$TYPE_NAME as TYPE_NAME
            FROM RDB$RELATION_FIELDS f
            LEFT JOIN RDB$TYPES t ON f.RDB$FIELD_TYPE = t.RDB$TYPE
                AND t.RDB$FIELD_NAME = 'RDB$FIELD_TYPE'
            WHERE f.RDB$RELATION_NAME = ?
            ORDER BY f.RDB$FIELD_POSITION
        """
        
        results = self.execute_query(query, (table_name.upper(),))
        
        schema = []
        for row in results:
            schema.append({
                "name": row['FIELD_NAME'].strip() if row['FIELD_NAME'] else '',
                "type": row['TYPE_NAME'].strip() if row['TYPE_NAME'] else 'UNKNOWN',
                "nullable": row['NULL_FLAG'] != 1
            })
        
        logger.info(f"Retrieved schema for table {table_name}: {len(schema)} columns")
        return schema


# Глобальный экземпляр БД
db: Optional[FirebirdDatabase] = None


def initialize_database() -> FirebirdDatabase:
    """
    Инициализация глобального экземпляра БД из настроек.
    
    Returns:
        FirebirdDatabase: Инициализированный экземпляр
    """
    global db
    
    db = FirebirdDatabase(
        host=settings.db_host,
        port=settings.db_port,
        database=settings.db_name,
        user=settings.db_user,
        password=settings.db_password,
        connection_timeout=settings.db_connection_timeout,
        cache_ttl=getattr(settings, 'cache_ttl', 300)
    )
    
    logger.info("Database initialized successfully")
    return db


def get_database() -> FirebirdDatabase:
    """
    Dependency для FastAPI - получение экземпляра БД.
    
    Returns:
        FirebirdDatabase: Глобальный экземпляр БД
        
    Raises:
        RuntimeError: Если БД не инициализирована
    """
    if db is None:
        raise RuntimeError(
            "Database not initialized. "
            "Call initialize_database() on application startup."
        )
    return db


def clear_cache():
    """Очистить весь кеш запросов"""
    global _query_cache
    count = len(_query_cache)
    _query_cache.clear()
    logger.info(f"Cache cleared: {count} entries removed")

