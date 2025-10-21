#!/usr/bin/env python3
"""
Генератор Bearer Token для API аутентификации

Использование:
    python scripts/generate_token.py
    python scripts/generate_token.py --length 64
"""

import secrets
import argparse


def generate_token(length: int = 32) -> str:
    """
    Генерация криптографически безопасного токена.
    
    Args:
        length: Длина токена в байтах (итоговая строка будет длиннее)
        
    Returns:
        str: Hex строка токена
    """
    return secrets.token_hex(length)


def main():
    parser = argparse.ArgumentParser(
        description="Генератор Bearer Token для API"
    )
    parser.add_argument(
        "--length",
        type=int,
        default=32,
        help="Длина токена в байтах (по умолчанию: 32)"
    )
    parser.add_argument(
        "--count",
        type=int,
        default=1,
        help="Количество токенов для генерации (по умолчанию: 1)"
    )
    
    args = parser.parse_args()
    
    print(f"\n{'='*60}")
    print(f"Генерация {args.count} токен(ов) длиной {args.length} байт")
    print(f"{'='*60}\n")
    
    tokens = []
    for i in range(args.count):
        token = generate_token(args.length)
        tokens.append(token)
        print(f"Token {i+1}: {token}")
    
    if args.count > 1:
        print(f"\n{'='*60}")
        print("Для .env файла (несколько токенов):")
        print(f"{'='*60}")
        print(f"API_TOKENS={','.join(tokens)}")
    else:
        print(f"\n{'='*60}")
        print("Для .env файла:")
        print(f"{'='*60}")
        print(f"API_TOKENS={tokens[0]}")
    
    print(f"\n{'='*60}")
    print("⚠️  ВАЖНО: Сохраните токен в безопасном месте!")
    print("⚠️  Никогда не коммитьте токены в Git!")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()

