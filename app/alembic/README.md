# Alembic для HP

## Переменная окружения

Для backend задайте `DATABASE_URL`, например:

```env
DATABASE_URL=postgresql+asyncpg://hp_user:password@postgres:5432/hp_db
```

Имя хоста `postgres` должно совпадать с именем PostgreSQL-сервиса в Docker Compose.
Не храните настоящий пароль в Git.

## Команды

Из каталога `backend/`:

```bash
alembic revision --autogenerate -m "initial schema"
alembic upgrade head
alembic current
alembic history
alembic downgrade -1
```

Перед созданием первой миграции проверьте, что все модели импортированы в `alembic/env.py`,
а `Base` импортируется из того же модуля, который используют модели приложения.

Autogenerate создаёт черновик миграции. Всегда просматривайте файл в `alembic/versions/`
перед применением.

Если база уже содержит таблицы, не запускайте начальную миграцию поверх неё вслепую.
Сначала нужно сравнить реальную схему с миграцией и только затем решать, нужен ли `alembic stamp`.
