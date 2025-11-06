#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестирование API в production окружении

Использование:
    python scripts/test_api_production.py --url http://85.114.224.45:8000 --token YOUR_TOKEN
"""

import sys
import argparse
import requests
from typing import Optional

# Настройка кодировки для Windows консоли
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, "strict")
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.buffer, "strict")


def test_health(url: str) -> bool:
    """Тест 1: Health check (без токена)"""
    print("\n" + "=" * 60)
    print("ТЕСТ 1: Health Check (без токена)")
    print("=" * 60)
    
    try:
        response = requests.get(f"{url}/api/health", timeout=10)
        print(f"URL: {url}/api/health")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {data}")
            print("✓ Health check успешен!")
            return True
        else:
            print(f"✗ Ошибка: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Ошибка подключения: {e}")
        return False


def test_query_with_token(url: str, token: str) -> bool:
    """Тест 2: Query с токеном"""
    print("\n" + "=" * 60)
    print("ТЕСТ 2: Query с токеном")
    print("=" * 60)
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Простой SELECT запрос
    query_data = {
        "query": "SELECT COUNT(*) as total FROM RDB$DATABASE"
    }
    
    try:
        print(f"URL: {url}/api/query")
        print(f"Query: {query_data['query']}")
        
        response = requests.post(
            f"{url}/api/query",
            json=query_data,
            headers=headers,
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {data}")
            print("✓ Query успешен!")
            return True
        else:
            print(f"✗ Ошибка: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Ошибка: {e}")
        return False


def test_query_without_token(url: str) -> bool:
    """Тест 3: Query без токена (должна быть ошибка 401)"""
    print("\n" + "=" * 60)
    print("ТЕСТ 3: Query без токена (ожидается ошибка 401)")
    print("=" * 60)
    
    query_data = {
        "query": "SELECT COUNT(*) FROM RDB$DATABASE"
    }
    
    try:
        response = requests.post(
            f"{url}/api/query",
            json=query_data,
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code in [401, 403]:  # FastAPI может вернуть 403 для отсутствующей аутентификации
            print("✓ Правильно отклонен запрос без токена!")
            return True
        else:
            print(f"✗ Неожиданный статус: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Ошибка: {e}")
        return False


def test_invalid_token(url: str) -> bool:
    """Тест 4: Query с неверным токеном (должна быть ошибка 401)"""
    print("\n" + "=" * 60)
    print("ТЕСТ 4: Query с неверным токеном (ожидается ошибка 401)")
    print("=" * 60)
    
    headers = {
        "Authorization": "Bearer invalid-token-12345",
        "Content-Type": "application/json"
    }
    
    query_data = {
        "query": "SELECT COUNT(*) FROM RDB$DATABASE"
    }
    
    try:
        response = requests.post(
            f"{url}/api/query",
            json=query_data,
            headers=headers,
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 401:
            print("✓ Правильно отклонен запрос с неверным токеном!")
            return True
        else:
            print(f"✗ Неожиданный статус: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Ошибка: {e}")
        return False


def test_get_tables(url: str, token: str) -> bool:
    """Тест 5: Получить список таблиц"""
    print("\n" + "=" * 60)
    print("ТЕСТ 5: Получить список таблиц")
    print("=" * 60)
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        # Попробуем разные варианты пути
        endpoints = [
            f"{url}/api/info/tables",
            f"{url}/api/tables",
            f"{url}/api/info",
        ]
        
        response = None
        for endpoint in endpoints:
            try:
                response = requests.get(endpoint, headers=headers, timeout=30)
                if response.status_code == 200:
                    break
            except:
                continue
        
        if response is None:
            print("✗ Не удалось найти endpoint для списка таблиц")
            return False
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            tables = data.get("tables", [])
            print(f"Найдено таблиц: {len(tables)}")
            if tables:
                print("Первые 10 таблиц:")
                for i, table in enumerate(tables[:10], 1):
                    print(f"  {i}. {table}")
            print("✓ Получение списка таблиц успешно!")
            return True
        else:
            print(f"✗ Ошибка: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Ошибка: {e}")
        return False


def test_dangerous_query(url: str, token: str) -> bool:
    """Тест 6: Опасный запрос (UPDATE/DELETE) - должна быть ошибка"""
    print("\n" + "=" * 60)
    print("ТЕСТ 6: Опасный запрос (UPDATE) - ожидается ошибка 400")
    print("=" * 60)
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Попытка выполнить UPDATE (должна быть отклонена)
    query_data = {
        "query": "UPDATE RDB$DATABASE SET RDB$DESCRIPTION = 'test'"
    }
    
    try:
        response = requests.post(
            f"{url}/api/query",
            json=query_data,
            headers=headers,
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            # Проверяем что запрос был отклонен (success=false и есть ошибка)
            if not data.get("success", True) and "error" in data:
                error_msg = data.get("error", "")
                if "Forbidden operation" in error_msg or "UPDATE" in error_msg or "DELETE" in error_msg:
                    print("✓ Опасный запрос правильно отклонен!")
                    print(f"Error message: {error_msg}")
                    return True
        
        print(f"✗ Неожиданный ответ")
        print(f"Response: {response.text}")
        return False
    except Exception as e:
        print(f"✗ Ошибка: {e}")
        return False


def test_real_query(url: str, token: str) -> bool:
    """Тест 7: Реальный запрос к таблице"""
    print("\n" + "=" * 60)
    print("ТЕСТ 7: Реальный запрос к таблице")
    print("=" * 60)
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Запрос к системной таблице (должна существовать)
    query_data = {
        "query": "SELECT FIRST 5 RDB$RELATION_NAME FROM RDB$RELATIONS WHERE RDB$SYSTEM_FLAG = 0"
    }
    
    try:
        print(f"Query: {query_data['query']}")
        response = requests.post(
            f"{url}/api/query",
            json=query_data,
            headers=headers,
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            rows = data.get("rows", [])
            print(f"Получено строк: {len(rows)}")
            if rows:
                print("Первые строки:")
                for i, row in enumerate(rows[:3], 1):
                    print(f"  {i}. {row}")
            print("✓ Реальный запрос успешен!")
            return True
        else:
            print(f"✗ Ошибка: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Ошибка: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Тестирование Firebird DB Proxy API")
    parser.add_argument(
        "--url",
        default="http://85.114.224.45:8000",
        help="URL API сервера (по умолчанию: http://85.114.224.45:8000)"
    )
    parser.add_argument(
        "--token",
        required=True,
        help="API токен для аутентификации"
    )
    
    args = parser.parse_args()
    
    url = args.url.rstrip("/")
    token = args.token.strip()
    
    print("\n" + "=" * 60)
    print("ТЕСТИРОВАНИЕ FIREBIRD DB PROXY API")
    print("=" * 60)
    print(f"URL: {url}")
    print(f"Token: {token[:20]}...{token[-10:]}")
    print("=" * 60)
    
    results = []
    
    # Запуск всех тестов
    results.append(("Health Check", test_health(url)))
    results.append(("Query с токеном", test_query_with_token(url, token)))
    results.append(("Query без токена", test_query_without_token(url)))
    results.append(("Неверный токен", test_invalid_token(url)))
    results.append(("Список таблиц", test_get_tables(url, token)))
    results.append(("Опасный запрос", test_dangerous_query(url, token)))
    results.append(("Реальный запрос", test_real_query(url, token)))
    
    # Итоги
    print("\n" + "=" * 60)
    print("ИТОГИ ТЕСТИРОВАНИЯ")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print("=" * 60)
    print(f"Пройдено: {passed}/{total}")
    
    if passed == total:
        print("✓ ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        return 0
    else:
        print(f"✗ НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОЙДЕНЫ ({total - passed} из {total})")
        return 1


if __name__ == "__main__":
    sys.exit(main())

