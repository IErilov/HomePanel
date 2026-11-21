home-portal/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── security.py
│   │   │   └── permissions.py
│   │   │
│   │   ├── db/
│   │   │   ├── database.py
│   │   │   ├── models/
│   │   │   └── migrations/
│   │   │
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── auth.py
│   │   │       ├── admin.py
│   │   │       ├── storage.py
│   │   │       ├── public.py
│   │   │       └── home_assistant.py
│   │   │
│   │   ├── storage/
│   │   │   ├── manager.py
│   │   │   ├── bucket_service.py
│   │   │   ├── upload_service.py
│   │   │   ├── file_service.py
│   │   │   ├── download_service.py
│   │   │   ├── organizer.py
│   │   │   └── minio_client.py
│   │   │
│   │   ├── integrations/
│   │   │   └── home_assistant.py
│   │   │
│   │   └── schemas/
│   │
│   ├── alembic.ini
│   ├── pyproject.toml
│   └── Dockerfile
│
├── frontend/
│   └── ...
│
├── infrastructure/
│   ├── compose.yaml
│   └── Caddyfile
│
├── .env.example
└── README.md