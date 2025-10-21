/*
  СОЗДАНИЕ READ-ONLY ПОЛЬЗОВАТЕЛЯ ДЛЯ API
  
  Этот скрипт создает пользователя с правами только на чтение.
  Выполнить от имени SYSDBA в базе DK_GEORGIA.
  
  Дата: 2025-10-21
  Проект: Firebird Database Proxy API
*/

-- ============================================================
-- 1. СОЗДАНИЕ ПОЛЬЗОВАТЕЛЯ
-- ============================================================

CREATE USER api_readonly PASSWORD 'Api#ReadOnly#2025!Secure';

COMMIT;

-- ============================================================
-- 2. ПРАВА НА ОСНОВНЫЕ ТАБЛИЦЫ (для анализа продаж кофе)
-- ============================================================

-- Группы магазинов
GRANT SELECT ON STORGRP TO api_readonly;

-- Заказы
GRANT SELECT ON STORZAKAZDT TO api_readonly;

-- Детали заказов с товарами
GRANT SELECT ON STORZDTGDS TO api_readonly;

-- Товары
GRANT SELECT ON GOODS TO api_readonly;

COMMIT;

-- ============================================================
-- 3. ПРАВА НА СИСТЕМНЫЕ ТАБЛИЦЫ
-- (нужны для работы API endpoints: /api/tables, /api/schema)
-- ============================================================

GRANT SELECT ON RDB$RELATIONS TO api_readonly;
GRANT SELECT ON RDB$RELATION_FIELDS TO api_readonly;
GRANT SELECT ON RDB$FIELDS TO api_readonly;
GRANT SELECT ON RDB$TYPES TO api_readonly;
GRANT SELECT ON RDB$DATABASE TO api_readonly;

COMMIT;

-- ============================================================
-- 4. ДОПОЛНИТЕЛЬНЫЕ ТАБЛИЦЫ (если нужны)
-- ============================================================

-- Если нужен доступ к другим таблицам, добавьте здесь:
-- GRANT SELECT ON YOUR_TABLE_NAME TO api_readonly;

COMMIT;

-- ============================================================
-- 5. ПРОВЕРКА
-- ============================================================

-- Проверить что пользователь создан
SELECT 
    RDB$USER_NAME AS USERNAME,
    RDB$FIRST_NAME AS FIRST_NAME,
    RDB$MIDDLE_NAME AS MIDDLE_NAME,
    RDB$LAST_NAME AS LAST_NAME
FROM RDB$USERS 
WHERE RDB$USER_NAME = 'API_READONLY';

-- Должен показать одну строку с API_READONLY

-- ============================================================
-- 6. ТЕСТ ДОСТУПА
-- ============================================================

/*
  После выполнения этого скрипта, ОТКЛЮЧИТЕСЬ и подключитесь заново как api_readonly:
  
  CONNECT localhost/3055:DK_GEORGIA USER api_readonly PASSWORD 'Api#ReadOnly#2025!Secure';
  
  Затем проверьте:
  
  -- Должно работать (SELECT)
  SELECT COUNT(*) FROM STORGRP;
  
  -- Должна быть ошибка (UPDATE заблокирован)
  UPDATE STORGRP SET NAME = 'Test' WHERE ID = 1;
  -- Ожидаем: no permission for UPDATE access to TABLE STORGRP
  
  Если получили ошибку на UPDATE - ВСЕ ПРАВИЛЬНО! ✅
  Пользователь может только читать, не может изменять.
*/

-- ============================================================
-- ВАЖНАЯ ИНФОРМАЦИЯ ДЛЯ .env ФАЙЛА
-- ============================================================

/*
  Использовать в .env файле API:
  
  DB_USER=api_readonly
  DB_PASSWORD=Api#ReadOnly#2025!Secure
  
  НЕ использовать SYSDBA в production!
*/

