# RadioChWeb — Architecture

This repository hosts RadioChWeb, a Flask application for discovering, analyzing, validating and managing radio stream sources. This document gives a concise, public-facing overview of the project's structure, main components, and how to run and contribute.

## Repository layout (top-level)

```
RadioChWeb/
├── app.py                    # Flask application entry point
├── database.py               # SQLAlchemy + database helpers
├── requirements.txt          # Pinned Python dependencies
├── migrate_db/               # SQL migration scripts and runner (pyway)
├── model/                    # Domain models, DTOs and repositories
│   ├── dto/                  # Pydantic DTOs used by services and views
│   ├── entity/               # SQLAlchemy ORM models
│   └── repository/           # Repository classes (data access)
├── route/                    # Flask Blueprints (HTTP routes)
├── service/                  # Business logic / service layer
├── templates/                # Jinja2 HTML templates used by the web UI
├── static/                   # Static assets (css, images, js)
├── specs/                    # Implementation specs and usage notes
├── tests/                    # pytest test-suite (unit and integration)
└── README.md                 # Project readme and basic instructions
```

## High-level components

- Presentation: Flask + Jinja2 templates provide web routes for listing sources, viewing and managing proposals, and running stream analysis. A minimal Textual-based terminal UI is included for development.
- Service layer: Business logic is implemented in `service/` modules (e.g. stream analysis, proposals, radio source management). Services operate on DTOs and entities and use repositories for persistence.
- Model layer: Domain models live in `model/entity` (SQLAlchemy ORM). DTOs (Pydantic v2) live in `model/dto` and are used to validate and serialize data passed between layers.
- Data access: Repository classes in `model/repository` encapsulate database access and queries.
- Migrations: `migrate_db/` contains SQL migration files and a small runner that can be used to apply migrations.

## Technology stack

- Python (3.10+ recommended)
- Flask — web framework
- SQLAlchemy — ORM and session management
- Pydantic v2 — DTOs and validation
- PyWay or SQL migration files in `migrate_db/` — migration runner
- pytest — unit and integration testing
- Optional: `ffmpeg` and `curl` are used by stream analysis tools when present on the host

## Database

- Default development database: SQLite (local file). Use migration SQL files under `migrate_db/migrations` to create or update schema.

## Runtime / development

Quick start (development):

```bash
git clone <repo_url>
cd RadioChWeb
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# initialize or migrate the database
python migrate_db/migrate.py

# run tests
pytest -q

# run the web app in development
python app.py
```

Notes:
- The development server is not suitable for production. Use a WSGI server (gunicorn, uvicorn) for production deployments.
- External binaries (ffmpeg, curl) are optional but enable richer stream analysis features.

## Tests and CI

- Tests are implemented with `pytest`. Fixtures are in `tests/conftest.py`.
- A typical CI job should install `requirements.txt` and run `pytest -q`.

## Contributing

- Follow the specs in `specs/` when adding or changing functionality.
- Add tests for new service logic and route behavior.
- For schema changes, add SQL migration files under `migrate_db/migrations`.

---

**Last updated**: 2025-12-11

If you want an API reference, an entity diagram, or a short HOWTO for deploying to production, I can add those sections.

*** End Public Architecture Overview ***


#### **Quality Assurance** 🔍
