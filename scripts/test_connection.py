#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест подключения к Firebird БД

Использование:
    python scripts/test_connection.py
"""

import sys
import os

# Настройка кодировки для Windows консоли
if sys.platform == "win32":
    import codecs

    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, "strict")
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.buffer, "strict")

# Добавить родительскую директорию в путь для импорта app модулей
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import settings
from app.database import FirebirdDatabase


def test_connection():
    """Тест подключения к БД"""

    print("\n" + "=" * 60)
    print("ТЕСТ ПОДКЛЮЧЕНИЯ К FIREBIRD БД")
    print("=" * 60 + "\n")

    print(f"Хост:     {settings.db_host}")
    print(f"Порт:     {settings.db_port}")
    print(f"База:     {settings.db_name}")
    print(f"DSN:      {settings.db_dsn}")
    print(f"User:     {settings.db_user}")
    print(f"Password: {'*' * min(len(settings.db_password), 10)}")

    print("\n" + "-" * 60)
    print("Создание пула соединений...")
    print("-" * 60 + "\n")

    try:
        db = FirebirdDatabase(
            host=settings.db_host,
            port=settings.db_port,
            database=settings.db_name,
            user=settings.db_user,
            password=settings.db_password,
            connection_timeout=settings.db_connection_timeout,
        )

        print("✓ Database инициализирована успешно\n")

        print("-" * 60)
        print("Тест подключения...")
        print("-" * 60 + "\n")

        if db.test_connection():
            print("✓ Подключение успешно!\n")

            print("-" * 60)
            print("Получение списка таблиц...")
            print("-" * 60 + "\n")

            tables = db.get_tables()
            print(f"✓ Найдено таблиц: {len(tables)}\n")

            if tables:
                print("Первые 10 таблиц:")
                for i, table in enumerate(tables[:10], 1):
                    print(f"  {i}. {table}")

                if len(tables) > 10:
                    print(f"  ... и еще {len(tables) - 10} таблиц")

            print("\n" + "=" * 60)
            print("ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО! ✓")
            print("=" * 60 + "\n")

            return True
        else:
            print("✗ Тест подключения не удался\n")
            print("=" * 60)
            print("ТЕСТ НЕ ПРОЙДЕН ✗")
            print("=" * 60 + "\n")
            return False

    except Exception as e:
        print(f"✗ Ошибка: {e}\n")
        print("=" * 60)
        print("ТЕСТ НЕ ПРОЙДЕН ✗")
        print("=" * 60 + "\n")
        return False


if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
