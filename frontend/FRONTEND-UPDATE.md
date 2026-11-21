# Home portal by Erilov Ilya — frontend

Минималистичный интерфейс файлового портала на Vue 3 + Vite.

## Навигация
- `/` — автоматически открывает `/app`, если в браузере есть `hp_access_token`, иначе `/login`.
- `/app` — единственная рабочая страница: файловое пространство со списком доступных бакетов и файлов.
- `/login` — вход в существующий аккаунт. Если токен уже есть, переход на `/app`.
- `/register` — перенаправление на `/login`; регистрации в интерфейсе нет.

В боковом меню оставлена только ссылка «Файловое пространство». Выбор доступного бакета остаётся внутри этой страницы.

## Возможности файловой страницы
- просмотр доступных хранилищ и файлов;
- поиск и сортировка;
- загрузка и скачивание;
- переименование и удаление с учётом прав backend;
- светлая и тёмная темы.

## API
Используются существующие endpoints:
- `POST /api/users/login`
- `GET /api/users/me`
- `GET /api/buckets/`
- `GET /api/buckets/{bucket_id}/files`
- `POST /api/buckets/{bucket_id}/upload`
- `GET /api/buckets/{bucket_id}/download/{filename}`
- `DELETE /api/buckets/{bucket_id}/files/{filename}`
- `PATCH /api/buckets/{bucket_id}/files/{filename}`

Backend должен предоставлять `GET /api/buckets/`: гостю — доступные OPEN бакеты, авторизованному пользователю — OPEN и его PERSONAL бакеты.

## Сборка
```bash
npm install
npm run build
```

В Docker сборка выполняется frontend Dockerfile.
