
# SQLAlchemy 2.0 — практическая шпаргалка

## 1. Что такое SQLAlchemy?

SQLAlchemy — Python-библиотека для работы с реляционными базами данных.

Она позволяет:
- Создавать таблицы через Python-классы.
- Выполнять SQL-запросы через Python.
- Добавлять, изменять и удалять записи.
- Управлять транзакциями.
- Связывать таблицы между собой.

SQLAlchemy имеет две основные части:

1. Core — работа с SQL-выражениями и таблицами.
2. ORM — работа с базой через Python-объекты и модели.

В нашем проекте мы преимущественно используем ORM.

---

# 2. Подключение к базе данных

## Обычный SQL

Для подключения к PostgreSQL приложению необходимо установить соединение с сервером БД.

## SQLAlchemy

```python
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession
)

DATABASE_URL = "postgresql+asyncpg://user:password@localhost:5432/database"

engine = create_async_engine(
    DATABASE_URL,
    echo=True
)

async_session = async_sessionmaker(
    engine,
    expire_on_commit=False
)
```

### Что такое engine?

`engine` — объект, который управляет подключениями к базе данных.

Он отвечает за создание и выдачу соединений.

### Что такое AsyncSession?

`AsyncSession` — объект, через который выполняются запросы и управляются транзакции.

Пример получения сессии:

```python
async with async_session() as session:
    ...
```

Сессия используется для работы с БД в рамках определённой задачи.

Важно: `Session` и `AsyncSession` не одно и то же. При асинхронной работе используем `await` для операций, которые выполняются асинхронно.

---

# 3. Создание моделей

ORM-модель — Python-класс, который соответствует таблице в базе данных.

## Обычный SQL

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL
);
```

## SQLAlchemy

```python
import uuid

from sqlalchemy import String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4
    )

    name: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False
    )
```

### Основные параметры mapped_column()

| Параметр | Назначение |
|---|---|
| `primary_key=True` | Первичный ключ |
| `nullable=False` | Запрещает NULL |
| `unique=True` | Запрещает дубликаты |
| `default=value` | Значение по умолчанию на стороне Python |
| `server_default=value` | Значение по умолчанию на стороне БД |
| `index=True` | Создаёт индекс |
| `ForeignKey()` | Создаёт внешний ключ |

### Типы данных

| SQLAlchemy | SQL | Назначение |
|---|---|---|
| `String(50)` | VARCHAR(50) | Строка |
| `Text` | TEXT | Большой текст |
| `Integer` | INTEGER | Целое число |
| `BigInteger` | BIGINT | Большое целое |
| `Boolean` | BOOLEAN | True / False |
| `DateTime` | TIMESTAMP | Дата и время |
| `Uuid` | UUID | Уникальный идентификатор |
| `JSON` | JSON | JSON-данные |
| `Enum` | ENUM | Перечисление |

---

# 4. Добавление записей — INSERT

## Обычный SQL

```sql
INSERT INTO users (name, email)
VALUES ('Alex', 'alex@example.com');
```

## SQLAlchemy

```python
user = User(
    name="Alex",
    email="alex@example.com"
)

session.add(user)

await session.commit()
```

### Разбор

`User()` — создаёт Python-объект.

`session.add(user)` — добавляет объект в текущую сессию.

`await session.commit()` — фиксирует изменения в базе данных.

Важно: `add()` не выполняет немедленную запись в БД. Изменения отправляются при `flush()` или `commit()`.

### flush()

```python
session.add(user)

await session.flush()
```

`flush()` отправляет накопленные изменения в БД, но не завершает транзакцию.

Например, после `flush()` можно получить автоматически созданный ID и продолжить работать в той же транзакции.

### refresh()

```python
await session.refresh(user)
```

Обновляет объект данными из БД.

Полезно, когда нужно получить значения, которые выставила сама база данных.

---

# 5. Получение записей — SELECT

## Получить все записи

### SQL

```sql
SELECT * FROM users;
```

### SQLAlchemy

```python
from sqlalchemy import select

query = select(User)

result = await session.execute(query)

users = result.scalars().all()
```

### Разбор

`select(User)` — формирует запрос на получение объектов User.

`execute()` — выполняет запрос.

`scalars()` — извлекает ORM-объекты из результата.

`all()` — получает все найденные записи.

---

## Получить одну запись по ID

### SQL

```sql
SELECT * FROM users
WHERE id = 'some-uuid';
```

### SQLAlchemy

```python
query = select(User).where(
    User.id == user_id
)

result = await session.execute(query)

user = result.scalar_one_or_none()
```

`scalar_one_or_none()`:
- Возвращает объект, если найдена одна запись.
- Возвращает None, если ничего не найдено.
- Выбрасывает исключение, если найдено больше одной записи.

---

# 6. WHERE — фильтрация

## SQL

```sql
SELECT * FROM events
WHERE user_id = 'some-uuid';
```

## SQLAlchemy

```python
query = select(Events).where(
    Events.user_id == user_id
)

result = await session.execute(query)

events = result.scalars().all()
```

### Несколько условий — AND

SQL:

```sql
SELECT * FROM events
WHERE user_id = 'some-uuid'
AND event_type = 'upload';
```

SQLAlchemy:

```python
query = select(Events).where(
    Events.user_id == user_id,
    Events.event_type == EventType.UPLOAD
)
```

Несколько аргументов внутри `where()` объединяются через AND.

### OR

SQL:

```sql
SELECT * FROM events
WHERE event_type = 'upload'
OR event_type = 'download';
```

SQLAlchemy:

```python
from sqlalchemy import or_

query = select(Events).where(
    or_(
        Events.event_type == EventType.UPLOAD,
        Events.event_type == EventType.DOWNLOAD
    )
)
```

Можно использовать `|`:

```python
query = select(Events).where(
    (Events.event_type == EventType.UPLOAD) |
    (Events.event_type == EventType.DOWNLOAD)
)
```

Важно: каждое условие при использовании `|` необходимо заключать в скобки.

### IN

SQL:

```sql
SELECT * FROM events
WHERE event_type IN ('upload', 'download');
```

SQLAlchemy:

```python
query = select(Events).where(
    Events.event_type.in_([
        EventType.UPLOAD,
        EventType.DOWNLOAD
    ])
)
```

### NOT

SQL:

```sql
SELECT * FROM events
WHERE event_type != 'upload';
```

SQLAlchemy:

```python
query = select(Events).where(
    Events.event_type != EventType.UPLOAD
)
```

---

# 7. ORDER BY — сортировка

## SQL

```sql
SELECT * FROM events
ORDER BY created_at DESC;
```

## SQLAlchemy

```python
query = select(Events).order_by(
    Events.created_at.desc()
)
```

### ASC и DESC

| SQL | SQLAlchemy | Значение |
|---|---|---|
| ASC | `.asc()` | По возрастанию |
| DESC | `.desc()` | По убыванию |

Пример:

```python
query = select(Events).order_by(
    Events.created_at.asc()
)
```

---

# 8. LIMIT и OFFSET — ограничение результатов

## SQL

```sql
SELECT * FROM events
LIMIT 100;
```

## SQLAlchemy

```python
query = select(Events).limit(100)
```

### OFFSET

SQL:

```sql
SELECT * FROM events
LIMIT 100 OFFSET 200;
```

SQLAlchemy:

```python
query = select(Events).limit(100).offset(200)
```

`LIMIT` — максимальное количество записей.

`OFFSET` — сколько записей пропустить.

Применяется для пагинации.

---

# 9. UPDATE — изменение записей

## SQL

```sql
UPDATE users
SET name = 'NewName'
WHERE id = 'some-uuid';
```

## SQLAlchemy ORM

```python
user = await session.get(User, user_id)

if user is not None:
    user.name = "NewName"

    await session.commit()
```

Здесь мы получаем объект и изменяем его атрибут.

SQLAlchemy отслеживает изменения объекта и отправляет UPDATE при сохранении транзакции.

### UPDATE через выражение

```python
from sqlalchemy import update

query = (
    update(User)
    .where(User.id == user_id)
    .values(name="NewName")
)

await session.execute(query)
await session.commit()
```

Такой вариант полезен для массовых изменений.

---

# 10. DELETE — удаление записей

## SQL

```sql
DELETE FROM users
WHERE id = 'some-uuid';
```

## SQLAlchemy ORM

```python
user = await session.get(User, user_id)

if user is not None:
    await session.delete(user)
    await session.commit()
```

Важно: `AsyncSession.delete()` — асинхронный метод, поэтому нужен `await`.

### DELETE через выражение

```python
from sqlalchemy import delete

query = delete(User).where(
    User.id == user_id
)

await session.execute(query)
await session.commit()
```

---

# 11. COUNT — подсчёт записей

## SQL

```sql
SELECT COUNT(*) FROM events;
```

## SQLAlchemy

```python
from sqlalchemy import select, func

query = select(func.count()).select_from(Events)

result = await session.execute(query)

count = result.scalar_one()
```

### Подсчёт событий конкретного пользователя

SQL:

```sql
SELECT COUNT(*)
FROM events
WHERE user_id = 'some-uuid';
```

SQLAlchemy:

```python
query = (
    select(func.count())
    .select_from(Events)
    .where(Events.user_id == user_id)
)

result = await session.execute(query)

count = result.scalar_one()
```

Это пригодится для аналитики количества загрузок.

---

# 12. SUM, AVG, MIN, MAX — агрегатные функции

SQL поддерживает функции для анализа числовых данных.

| Функция | Назначение |
|---|---|
| COUNT | Количество |
| SUM | Сумма |
| AVG | Среднее |
| MIN | Минимум |
| MAX | Максимум |

### Пример: общий размер загруженных файлов

SQL:

```sql
SELECT SUM(file_size)
FROM events
WHERE event_type = 'upload';
```

SQLAlchemy:

```python
query = (
    select(func.sum(Events.file_size))
    .where(Events.event_type == EventType.UPLOAD)
)

result = await session.execute(query)

total_size = result.scalar_one()
```

### Средний размер файла

```python
query = select(
    func.avg(Events.file_size)
)

result = await session.execute(query)

average_size = result.scalar_one()
```

---

# 13. GROUP BY — группировка

Очень важная операция для аналитики.

## SQL

Посчитать количество загрузок по каждому пользователю:

```sql
SELECT user_id, COUNT(*)
FROM events
WHERE event_type = 'upload'
GROUP BY user_id;
```

## SQLAlchemy

```python
query = (
    select(
        Events.user_id,
        func.count()
    )
    .where(Events.event_type == EventType.UPLOAD)
    .group_by(Events.user_id)
)

result = await session.execute(query)

statistics = result.all()
```

Результат будет содержать пары:

```text
(user_id, count)
```

Например:

```text
(UUID_1, 15)
(UUID_2, 8)
(UUID_3, 32)
```

Это уже основа для аналитических отчётов.

---

# 14. HAVING — фильтрация групп

`WHERE` фильтрует отдельные записи.

`HAVING` фильтрует результаты после GROUP BY.

## SQL

```sql
SELECT user_id, COUNT(*)
FROM events
GROUP BY user_id
HAVING COUNT(*) > 10;
```

## SQLAlchemy

```python
query = (
    select(
        Events.user_id,
        func.count()
    )
    .group_by(Events.user_id)
    .having(func.count() > 10)
)
```

В результате останутся только пользователи, у которых больше 10 событий.

---

# 15. JOIN — объединение таблиц

Допустим, у нас есть две таблицы:

users:

| id | name |
|---|---|
| 1 | Alex |
| 2 | John |

events:

| id | user_id | event_type |
|---|---|---|
| 1 | 1 | upload |
| 2 | 1 | download |
| 3 | 2 | upload |

Нам нужно получить имя пользователя и его действия.

## SQL

```sql
SELECT users.name, events.event_type
FROM events
JOIN users ON users.id = events.user_id;
```

## SQLAlchemy

```python
query = (
    select(User.name, Events.event_type)
    .join(User, Events.user_id == User.id)
)

result = await session.execute(query)

rows = result.all()
```

JOIN позволяет объединять данные из нескольких таблиц.

### Типы JOIN

| SQL | Назначение |
|---|---|
| INNER JOIN | Только совпавшие записи |
| LEFT JOIN | Все записи левой таблицы и совпадения справа |
| RIGHT JOIN | Все записи правой таблицы и совпадения слева |
| FULL JOIN | Все записи обеих таблиц |

---

# 16. ForeignKey и relationship

ForeignKey — внешний ключ, который связывает таблицы на уровне БД.

relationship — ORM-связь, позволяющая обращаться к связанным Python-объектам.

## SQL

```sql
CREATE TABLE events (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id)
);
```

## SQLAlchemy

В Events:

```python
user_id: Mapped[uuid.UUID | None] = mapped_column(
    ForeignKey("users.id"),
    nullable=True
)

user: Mapped["User | None"] = relationship(
    back_populates="events"
)
```

В User:

```python
events: Mapped[list["Events"]] = relationship(
    back_populates="user"
)
```

Теперь можно обращаться:

```python
event.user
```

И получать события пользователя:

```python
user.events
```

### Важное отличие

`ForeignKey` создаёт ограничение в БД.

`relationship` организует взаимодействие между объектами Python.

Одно не заменяет другое.

---

# 17. Работа с транзакциями

Транзакция — группа операций, которая должна выполниться согласованно.

Основные операции:

| Метод | Назначение |
|---|---|
| `commit()` | Зафиксировать изменения |
| `rollback()` | Отменить изменения |
| `flush()` | Отправить изменения в БД без завершения транзакции |
| `refresh()` | Обновить объект из БД |

### Пример

```python
try:
    session.add(user)

    await session.flush()

    await session.commit()

except Exception:
    await session.rollback()
    raise
```

Если возникает ошибка, `rollback()` отменяет изменения текущей транзакции.

### Контекстный менеджер транзакции

```python
async with session.begin():
    session.add(user)
    session.add(event)
```

При успешном завершении блока транзакция фиксируется автоматически.

При исключении выполняется откат.

---

# 18. Repository Pattern

Repository — слой, отвечающий за доступ к данным.

Он скрывает SQLAlchemy-запросы от остальных частей приложения.

Пример структуры:

```text
repo/
└── event_repository.py
```

Пример:

```python
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

class EventRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_user(self, user_id, limit=100):
        query = (
            select(Events)
            .where(Events.user_id == user_id)
            .order_by(Events.created_at.desc())
            .limit(limit)
        )

        result = await self.db.execute(query)

        return result.scalars().all()
```

Repository отвечает на вопрос:

**Как получить или сохранить данные?**

Он не должен решать, какие действия пользователя считать подозрительными.

---

# 19. Service Layer

Service содержит прикладную логику и координирует операции.

Пример структуры:

```text
services/
└── event_service.py
```

Пример:

```python
class EventService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = EventRepository(db)

    async def get_user_activity(self, user_id, limit=100):
        if not 1 <= limit <= 500:
            raise ValueError("Invalid limit")

        return await self.repository.get_by_user(
            user_id=user_id,
            limit=limit
        )
```

Service отвечает на вопрос:

**Что приложение должно сделать и в каком порядке?**

В более сложных операциях Service также управляет транзакцией.

---

# 20. Часто используемые методы AsyncSession

| Метод | Назначение | Асинхронный? |
|---|---|---|
| `add()` | Добавить объект в сессию | Нет |
| `add_all()` | Добавить несколько объектов | Нет |
| `execute()` | Выполнить SQL-запрос | Да |
| `get()` | Получить объект по PK | Да |
| `delete()` | Удалить объект | Да |
| `commit()` | Зафиксировать транзакцию | Да |
| `rollback()` | Откатить транзакцию | Да |
| `flush()` | Отправить изменения в БД | Да |
| `refresh()` | Обновить объект | Да |
| `close()` | Закрыть сессию | Да |

---

# 21. Полезные операторы SQLAlchemy

| SQLAlchemy | Значение |
|---|---|
| `==` | Равно |
| `!=` | Не равно |
| `>` | Больше |
| `<` | Меньше |
| `>=` | Больше или равно |
| `<=` | Меньше или равно |
| `.in_()` | IN |
| `.like()` | LIKE |
| `.ilike()` | ILIKE |
| `.is_(None)` | IS NULL |
| `.is_not(None)` | IS NOT NULL |
| `.between(a, b)` | BETWEEN |

Примеры:

```python
# Проверка NULL
Events.user_id.is_(None)

# Поиск по шаблону
User.email.ilike("%gmail.com")

# Диапазон значений
Events.file_size.between(1000, 5000)
```

---

# 22. Практические примеры для S3 Analyzer

### Получить последние 50 событий

```python
query = (
    select(Events)
    .order_by(Events.created_at.desc())
    .limit(50)
)
```

### Получить все загрузки пользователя

```python
query = select(Events).where(
    Events.user_id == user_id,
    Events.event_type == EventType.UPLOAD
)
```

### Посчитать загрузки за день

```python
query = (
    select(func.count())
    .select_from(Events)
    .where(
        Events.event_type == EventType.UPLOAD,
        Events.created_at >= start_date,
        Events.created_at < end_date
    )
)
```

### Получить пользователей с наибольшим количеством загрузок

```python
query = (
    select(
        Events.user_id,
        func.count().label("upload_count")
    )
    .where(Events.event_type == EventType.UPLOAD)
    .group_by(Events.user_id)
    .order_by(func.count().desc())
    .limit(10)
)
```

### Посчитать общий объём загруженных файлов

```python
query = (
    select(func.sum(Events.file_size))
    .where(Events.event_type == EventType.UPLOAD)
)
```

---

# 23. Главное, что нужно запомнить

| Компонент | Ответственность |
|---|---|
| Model | Описание таблицы |
| AsyncSession | Работа с БД и транзакциями |
| Repository | SQL-запросы и доступ к данным |
| Service | Прикладная логика |
| API | HTTP-запросы и ответы |

### Краткая шпаргалка SQL → SQLAlchemy

| SQL | SQLAlchemy |
|---|---|
| SELECT | `select()` |
| INSERT | `session.add()` |
| UPDATE | Изменение объекта или `update()` |
| DELETE | `session.delete()` или `delete()` |
| WHERE | `.where()` |
| ORDER BY | `.order_by()` |
| GROUP BY | `.group_by()` |
| HAVING | `.having()` |
| JOIN | `.join()` |
| LIMIT | `.limit()` |
| OFFSET | `.offset()` |
| COUNT | `func.count()` |
| SUM | `func.sum()` |
| AVG | `func.avg()` |

**Главный принцип:** SQLAlchemy не отменяет SQL. Она позволяет формировать SQL-запросы и работать с результатами через Python.
