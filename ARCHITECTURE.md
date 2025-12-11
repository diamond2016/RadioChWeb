# RadioChWeb Project Architecture

## Overview

RadioChWeb is a radio stream discovery and management application built following strict architectural principles. 
The project implements a backend-first, API-first approach with service-oriented design, using Flask, SQLAlchemy, and Python 3.14+.

## Project Structure

```
RadioChWeb/
├── 📁 specs/                          # Specification documents - Spec-Driven Development (SD-D)
│   ├── 📁 001-discover-radio-source/
│   ├── 📁 002-validate-and-add-radio-source/
│   ├── 📁 003-analyze-and-classify-stream/
│   └── 📁 model/
│   ├── ----📁 dto/                       # Data Transfer Objects
│   │   ----├── 📄 radio_source.py
│   │   ----├── 📄 stream_analysis.py
│   │   ----└── 📄 stream_type.py
    │   ├── 📁 entity/                     # SQLAlchemy ORM models
    │   │   ├── 📄 proposal.py
    │   │   ├── 📄 radio_source_node.py
    │   │   └── 📄 stream_type.py
    │   ├── 📁 repository/               # Data access layer
    │   │   ├── 📄 proposal_repository.py
    │   │   ├── 📄 radio_source_repository.py
    │   │   └── 📄 stream_type_repository.py
│   ├── 📁 route /                     # Flask API routes
│   ├── 📁 service/                    # Business logic layer
│   │   ├── 📄 proposal_validation_service.py  # Spec 002 validation
│   │   ├── 📄 radio_source_service.py         # Spec 002 save/reject
│   │   ├── 📄 stream_analysis_service.py
│   │   └── 📄 stream_type_service.py
│   └── 📁 static/                     # Static assets (planned)
    │   └── 📁 templates/                     # Static assets (planned)
    │   └── 📁 css/                     # Static assets (planned)
    │   └── 📁 js/                     # Static assets (planned)
    ├── 📁 tests/                          # Test suite
  │   ├── 📄 conftest.py                 # Test configuration
  │   ├── 📁 integration/                # Integration tests
  │   │   └── 📄 test_validate_and_add_workflow.py
  │   └── 📁 unit/                       # Unit tests
  │       ├── 📄 test_proposal_validation_service.py
  │       ├── 📄 test_radio_source_service.py
  │       └── 📄 test_stream_analysis_service.py
├── 📁 migration/                     # Database migrations (PyWay)
│   ├── 📄 V1_0__initial_schema.sql
│   └── 📄 V2_0__initialize_stream_types.sql
├── 📁 instance/                       # Database files
│   └── 📄 radio_sources.db.backup
│   ├── 📄 init_db.py                  # Database initialization & session management
|   !--    migrate.py                  # Database migrations (pyway)
├── 📄 radioch_app.py                  # Main Textual TUI application
├── 📄 migrate.py                      # Database migration runner
├── 📄 init_db.py                      # Database initialization
├── 📄 pyproject.toml                  # Python project configuration
├── 📄 requirements.txt                # Dependencies
├── 📄 pyway.yaml                      # PyWay migration configuration
└── 📄 work-in-progress.md             # Development notes
```

## Core Components

### 🏗️ Architecture Layers

#### 1. **Presentation Layer**
- **Web with Bootstrap/Flask**: Modern terminal-based user interface
- **Tabbed Interface**: Separate tabs for each specification (001, 002, 003)
- **Real-time Analysis**: Live stream analysis with progress feedback

#### 2. **Application Layer**
- **StreamAnalysisService**: Core business logic for stream validation
- **StreamTypeService**: Stream type classification and lookup
- **Flask API**: REST endpoints for service integration (planned)

#### 3. **Domain Layer**
- **RadioSourceNode**: Main entity representing radio sources
- **StreamType**: Lookup table with 14 predefined classifications
- **Proposal**: Temporary validation queue for new sources

#### 4. **Infrastructure Layer**
- **SQLAlchemy ORM**: Database abstraction and session management
- **SQLite Database**: Local data persistence
- **PyWay Migrations**: Database schema versioning

### 📊 Data Model

#### Core Entities
contains types of stream to be managed
**Stream Types**
CREATE TABLE stream_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    protocol VARCHAR(10) NOT NULL,  -- HTTP, HTTPS, HLS
    format VARCHAR(10) NOT NULL,    -- MP3, AAC, OGG
    metadata_type VARCHAR(15) NOT NULL,  -- Icecast, Shoutcast, None
    display_name VARCHAR(100) NOT NULL   -- Human-readable name
);

contains data of radio stream sources discovered and saved on db
**Radio Sources** 
CREATE TABLE radio_sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    streamUrl VARCHAR NOT NULL UNIQUE,
    name VARCHAR NOT NULL,
    websiteUrl VARCHAR,
    streamTypeId INTEGER NOT NULL,
    isSecure BOOLEAN NOT NULL DEFAULT 1,
    country VARCHAR,
    description VARCHAR,
    image VARCHAR,
    createdAt DATETIME DEFAULT CURRENT_TIMESTAMP,
    modifiedAt DATETIME,
    FOREIGN KEY (streamTypeId) REFERENCES stream_types(id)
);

contains proposals of discoreded radio sources ready to be saved in db
**Proposals**
CREATE TABLE IF NOT EXISTS "proposals" (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    streamUrl VARCHAR NOT NULL UNIQUE,
    name VARCHAR NOT NULL,
    websiteUrl VARCHAR,
    streamTypeId INTEGER,  -- Now allows NULL
    isSecure BOOLEAN NOT NULL DEFAULT 1,
    country VARCHAR,
    description VARCHAR,
    image VARCHAR,
    FOREIGN KEY (streamTypeId) REFERENCES stream_types(id)
);









*** Begin Public Architecture Overview ***

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
