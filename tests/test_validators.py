"""
Тесты валидации SQL запросов
"""

import pytest
from app.validators import validate_sql, sanitize_query


class TestValidateSQL:
    """Тесты функции validate_sql"""
    
    def test_select_allowed(self):
        """SELECT запросы должны быть разрешены"""
        query = "SELECT * FROM STORGRP"
        is_valid, error = validate_sql(query)
        assert is_valid is True
        assert error == "OK"
    
    def test_select_with_where_allowed(self):
        """SELECT с WHERE должен быть разрешен"""
        query = "SELECT ID, NAME FROM STORGRP WHERE ID = 1"
        is_valid, error = validate_sql(query)
        assert is_valid is True
    
    def test_select_with_join_allowed(self):
        """SELECT с JOIN должен быть разрешен"""
        query = """
            SELECT a.ID, b.NAME 
            FROM STORGRP a 
            JOIN GOODS b ON a.ID = b.STORE_ID
        """
        is_valid, error = validate_sql(query)
        assert is_valid is True
    
    def test_with_cte_allowed(self):
        """WITH (CTE) запросы должны быть разрешены"""
        query = """
            WITH temp AS (
                SELECT ID FROM STORGRP
            )
            SELECT * FROM temp
        """
        is_valid, error = validate_sql(query)
        assert is_valid is True
    
    def test_update_blocked(self):
        """UPDATE должен быть заблокирован"""
        query = "UPDATE STORGRP SET NAME = 'Test'"
        is_valid, error = validate_sql(query)
        assert is_valid is False
        assert "Forbidden" in error
        assert "UPDATE" in error.upper()
    
    def test_insert_blocked(self):
        """INSERT должен быть заблокирован"""
        query = "INSERT INTO STORGRP (NAME) VALUES ('Test')"
        is_valid, error = validate_sql(query)
        assert is_valid is False
        assert "Forbidden" in error
    
    def test_delete_blocked(self):
        """DELETE должен быть заблокирован"""
        query = "DELETE FROM STORGRP WHERE ID = 1"
        is_valid, error = validate_sql(query)
        assert is_valid is False
        assert "Forbidden" in error
    
    def test_drop_blocked(self):
        """DROP должен быть заблокирован"""
        query = "DROP TABLE STORGRP"
        is_valid, error = validate_sql(query)
        assert is_valid is False
        assert "Forbidden" in error
    
    def test_alter_blocked(self):
        """ALTER должен быть заблокирован"""
        query = "ALTER TABLE STORGRP ADD COLUMN test VARCHAR(100)"
        is_valid, error = validate_sql(query)
        assert is_valid is False
        assert "Forbidden" in error
    
    def test_truncate_blocked(self):
        """TRUNCATE должен быть заблокирован"""
        query = "TRUNCATE TABLE STORGRP"
        is_valid, error = validate_sql(query)
        assert is_valid is False
        assert "Forbidden" in error
    
    def test_execute_block_blocked(self):
        """EXECUTE BLOCK должен быть заблокирован"""
        query = "EXECUTE BLOCK AS BEGIN /* code */ END"
        is_valid, error = validate_sql(query)
        assert is_valid is False
        assert "Forbidden" in error
    
    def test_execute_procedure_blocked(self):
        """EXECUTE PROCEDURE должен быть заблокирован"""
        query = "EXECUTE PROCEDURE MY_PROC"
        is_valid, error = validate_sql(query)
        assert is_valid is False
        assert "Forbidden" in error
    
    def test_multiple_queries_blocked(self):
        """Множественные запросы через ; должны быть заблокированы"""
        query = "SELECT * FROM STORGRP; SELECT * FROM GOODS;"
        is_valid, error = validate_sql(query)
        assert is_valid is False
        assert "Forbidden" in error
    
    def test_comments_removed_single_line(self):
        """Однострочные комментарии должны удаляться"""
        query = """
            SELECT * FROM STORGRP -- это комментарий
            WHERE ID = 1
        """
        is_valid, error = validate_sql(query)
        assert is_valid is True
    
    def test_comments_removed_multi_line(self):
        """Многострочные комментарии должны удаляться"""
        query = """
            SELECT * FROM STORGRP
            /* это
               многострочный
               комментарий */
            WHERE ID = 1
        """
        is_valid, error = validate_sql(query)
        assert is_valid is True
    
    def test_update_in_comment_allowed(self):
        """UPDATE в комментарии не должен блокироваться"""
        query = """
            SELECT * FROM STORGRP
            -- UPDATE в комментарии
            WHERE ID = 1
        """
        is_valid, error = validate_sql(query)
        assert is_valid is True
    
    def test_empty_query_blocked(self):
        """Пустой запрос должен быть заблокирован"""
        query = ""
        is_valid, error = validate_sql(query)
        assert is_valid is False
        assert "Empty query" in error
    
    def test_whitespace_query_blocked(self):
        """Запрос из одних пробелов должен быть заблокирован"""
        query = "   \n\t  "
        is_valid, error = validate_sql(query)
        assert is_valid is False
    
    def test_case_insensitive(self):
        """Валидация должна быть регистронезависимой"""
        queries = [
            "select * from STORGRP",
            "SELECT * FROM storgrp",
            "SeLeCt * FrOm StOrGrP"
        ]
        for query in queries:
            is_valid, error = validate_sql(query)
            assert is_valid is True


class TestSanitizeQuery:
    """Тесты функции sanitize_query"""
    
    def test_remove_extra_spaces(self):
        """Лишние пробелы должны удаляться"""
        query = "SELECT  *   FROM    STORGRP"
        result = sanitize_query(query)
        assert result == "SELECT * FROM STORGRP"
    
    def test_remove_newlines(self):
        """Переносы строк должны заменяться на пробелы"""
        query = "SELECT *\nFROM\nSTORGRP"
        result = sanitize_query(query)
        assert "\n" not in result
    
    def test_trim_whitespace(self):
        """Пробелы в начале и конце должны удаляться"""
        query = "  SELECT * FROM STORGRP  "
        result = sanitize_query(query)
        assert result == "SELECT * FROM STORGRP"

