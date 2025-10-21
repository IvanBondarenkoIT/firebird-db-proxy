"""
Firebird database connection pool и операции с БД
"""

import fdb
import logging
from contextlib import contextmanager
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime

from app.config import settings

logger = logging.getLogger(__name__)


class FirebirdConnectionPool:
    """
    Connection pool для Firebird БД с автоматическим управлением соединениями.
    """
    
    def __init__(
        self,
        host: str,
        port: int,
        database: str,
        user: str,
        password: str,
        max_connections: int = 10,
        connection_timeout: int = 10
    ):
        """
        Инициализация пула соединений.
        
        Args:
            host: Хост Firebird сервера
            port: Порт Firebird сервера
            database: Имя БД или alias
            user: Пользователь БД
            password: Пароль пользователя
            max_connections: Максимальное количество соединений (не используется в простой реализации)
            connection_timeout: Таймаут подключения в секундах
        """
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.max_connections = max_connections
        self.connection_timeout = connection_timeout
        
        self.dsn = f"{host}/{port}:{database}"
        logger.info(f"Initialized Firebird connection pool: {self.dsn}")
        logger.info(f"Max connections: {max_connections}, Timeout: {connection_timeout}s")
    
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
        params: Optional[Tuple] = None
    ) -> List[Dict[str, Any]]:
        """
        Выполнение SELECT запроса и возврат результатов в виде списка словарей.
        
        Args:
            query: SQL запрос
            params: Параметры запроса (tuple для позиционных параметров)
            
        Returns:
            List[Dict[str, Any]]: Список строк в виде словарей {column_name: value}
            
        Raises:
            fdb.Error: Ошибки выполнения запроса
            
        Example:
            results = db_pool.execute_query(
                "SELECT ID, NAME FROM STORGRP WHERE ID = ?",
                (1,)
            )
            # [{"ID": 1, "NAME": "Магазин 1"}]
        """
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
                            # Преобразовать datetime в ISO формат для JSON
                            if isinstance(value, datetime):
                                value = value.isoformat()
                            row_dict[col_name] = value
                        results.append(row_dict)
                    
                    elapsed = (datetime.now() - start_time).total_seconds()
                    logger.info(
                        f"Query executed successfully: {len(results)} rows in {elapsed:.3f}s"
                    )
                    
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


# Глобальный экземпляр пула соединений
db_pool: Optional[FirebirdConnectionPool] = None


def initialize_db_pool() -> FirebirdConnectionPool:
    """
    Инициализация глобального пула соединений из настроек.
    
    Returns:
        FirebirdConnectionPool: Инициализированный пул
    """
    global db_pool
    
    db_pool = FirebirdConnectionPool(
        host=settings.db_host,
        port=settings.db_port,
        database=settings.db_name,
        user=settings.db_user,
        password=settings.db_password,
        max_connections=settings.db_max_connections,
        connection_timeout=settings.db_connection_timeout
    )
    
    logger.info("Database pool initialized successfully")
    return db_pool


def get_db_pool() -> FirebirdConnectionPool:
    """
    Dependency для FastAPI - получение экземпляра пула БД.
    
    Returns:
        FirebirdConnectionPool: Глобальный пул соединений
        
    Raises:
        RuntimeError: Если пул не инициализирован
    """
    if db_pool is None:
        raise RuntimeError(
            "Database pool not initialized. "
            "Call initialize_db_pool() on application startup."
        )
    return db_pool

