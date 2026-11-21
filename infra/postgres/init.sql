-- Расширения PostgreSQL для проекта HP

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Проверяем установленные расширения
SELECT extname
FROM pg_extension;