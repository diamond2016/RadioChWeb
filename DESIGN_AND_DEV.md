# RadioChWeb - Design and Development Documentation

## Project Overview

**RadioChWeb** is a comprehensive radio stream discovery, validation, and management web application built with Flask, SQLAlchemy, and modern Python practices. The project implements a spec-driven development approach with three core specifications:

1. **Spec 001**: Discover Radio Source - URL-based radio stream discovery
2. **Spec 002**: Validate and Add Radio Source - Proposal validation and database integration
3. **Spec 003**: Analyze and Classify Stream - Stream analysis and classification

## Table of Contents

1. [Project Constitution](#project-constitution)
2. [Architecture & Design](#architecture--design)
3. [Technology Stack](#technology-stack)
4. [Development Process](#development-process)
5. [Database Schema](#database-schema)
6. [API Endpoints](#api-endpoints)
7. [Data Transfer Objects (DTOs)](#data-transfer-objects-dtos)
8. [Repository Pattern Implementation](#repository-pattern-implementation)
9. [Service Layer](#service-layer)
10. [Web Interface](#web-interface)
11. [Testing Strategy](#testing-strategy)
12. [Deployment & Setup](#deployment--setup)
13. [Issues & Solutions](#issues--solutions)
14. [Future Development](#future-development)

## Project Constitution

### Core Principles

1. **Architecture**: Application logic resides in backend services
2. **API-First**: All services exposed via APIs as primary interaction method
3. **Decoupled Frontend/Backend**: Separate development and deployment
4. **Web Interface**: User interface built with Bootstrap and Flask templates
5. **Test-Driven Development**: Features implemented with failing tests first

### Technical Standards

- **Backend**: Flask framework with SQLAlchemy ORM
- **Database**: SQLite (with MySQL migration path planned)
- **Language**: Python 3.13+
- **Virtual Environment**: Required for all development
- **Testing**: pytest with assertion-based test cases
- **Data Exchange**: JSON payloads for service communication

## Architecture & Design

### Layered Architecture

```
┌─────────────────┐
│   Web Interface │ ← Bootstrap + Flask Templates
├─────────────────┤
│   API Routes    │ ← Flask Blueprints
├─────────────────┤
│  Service Layer  │ ← Business Logic
├─────────────────┤
│ Repository Layer│ ← Data Access
├─────────────────┤
│   Data Models   │ ← SQLAlchemy ORM
├─────────────────┤
│    Database     │ ← SQLite
└─────────────────┘
```

### Project Structure

```
RadioChWeb/
├── 📁 model/
│   ├── 📁 dto/           # Pydantic DTOs with v2.12.0
│   ├── 📁 entity/        # SQLAlchemy models
│   └── 📁 repository/    # Data access layer
├── 📁 route/             # Flask blueprint routes
├── 📁 service/           # Business logic services
├── 📁 templates/         # Bootstrap HTML templates
├── 📁 static/            # CSS, JS, images
├── 📁 specs/             # Specification documents
├── 📁 instance/          # SQLite database files
├── 📄 radioch_app.py     # Main Flask application
├── 📄 database.py        # SQLAlchemy instance
├── 📄 requirements.txt   # Python dependencies
└── 📄 DESIGN_AND_DEV.md  # This documentation
```

## Technology Stack

### Core Technologies

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| **Backend Framework** | Flask | 3.0.0 | Web framework and API server |
| **ORM** | SQLAlchemy | 2.0.44 | Database abstraction and queries |
| **ORM Extension** | Flask-SQLAlchemy | 3.1.1 | Flask integration for SQLAlchemy |
| **Data Validation** | Pydantic | 2.12.0 | DTO validation and serialization |
| **Database** | SQLite | 3.x | Data persistence |
| **Testing** | pytest | 8.0.0 | Unit and integration testing |
| **UI Framework** | Bootstrap | 5.3.0 | Responsive web interface |
| **Python** | Python | 3.14 | Runtime environment |

### Development Tools

- **Virtual Environment**: venv (Python built-in)
- **Version Control**: Git
- **Code Editor**: VS Code with Python extensions
- **API Testing**: curl, Postman (planned)

## Development Process

### Phase 1: Project Initialization (2025-11-29)

#### Step 1: Environment Setup
```bash
# Create project directory
mkdir RadioChWeb && cd RadioChWeb

# Initialize Python virtual environment
python -m venv .venv
source .venv/bin/activate

# Install core dependencies
pip install Flask==3.0.0 Flask-SQLAlchemy==3.1.1 SQLAlchemy==2.0.44 pydantic==2.12.0 pytest==8.0.0
```

#### Step 2: Database Design & Models
- Created separate `database.py` module to avoid circular imports
- Implemented SQLAlchemy models for core entities:
  - `StreamType`: Radio stream classifications
  - `RadioSource`: Discovered and validated radio sources
  - `Proposal`: Temporary validation queue

#### Step 3: Repository Pattern Implementation
- Created standardized repository classes with consistent methods:
  - `find_by_id(id)`: Retrieve by primary key
  - `find_all()`: Retrieve all records
  - `save(entity)`: Insert or update entity
  - `count()`: Count total records
- Implemented repository getter functions for proper session handling

#### Step 4: Pydantic DTO Integration
- Updated all DTOs to use Pydantic v2.12.0 `ConfigDict` syntax
- Created validation models for:
  - Stream analysis results
  - Stream type classifications
  - Data validation schemas

#### Step 5: Flask Blueprint Architecture
- Organized routes into logical blueprints:
  - `database_bp`: Core data endpoints (`/api/stats`, `/api/stream-types`)
  - `proposal_bp`: Proposal management (`/proposal/api/proposals`)
  - `radio_source_bp`: Source management (`/source/api/sources`)
- Registered blueprints with appropriate URL prefixes

#### Step 6: Bootstrap Web Interface
- Created responsive HTML templates using Bootstrap 5.3.0
- Implemented navigation and layout structure
- Prepared templates for dynamic data population

#### Step 7: Database Schema Alignment
- Manually added missing columns to existing SQLite database:
  - `radio_sources.modified_at` (DATETIME)
  - `proposals.stream_url` (VARCHAR)
  - `proposals.name` (VARCHAR)
  - `proposals.website_url` (VARCHAR)
  - `proposals.country` (VARCHAR)
  - `proposals.description` (VARCHAR)
  - `proposals.image_url` (VARCHAR)

#### Step 8: API Testing & Validation
- Verified all endpoints return proper JSON responses
- Confirmed database operations work correctly
- Validated session handling with repository getter functions

## Database Schema

### Stream Types Table
```sql
CREATE TABLE stream_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    protocol VARCHAR(10) NOT NULL,        -- HTTP, HTTPS, HLS
    format VARCHAR(10) NOT NULL,          -- MP3, AAC, OGG
    metadata_type VARCHAR(15) NOT NULL,   -- Icecast, Shoutcast, None
    display_name VARCHAR(100) NOT NULL    -- Human-readable name
);
```

### Radio Sources Table
```sql
CREATE TABLE radio_sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stream_url VARCHAR NOT NULL UNIQUE,
    name VARCHAR NOT NULL,
    website_url VARCHAR,
    stream_type_id INTEGER NOT NULL,
    is_secure BOOLEAN NOT NULL DEFAULT 1,
    country VARCHAR,
    description VARCHAR,
    image_url VARCHAR,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    modified_at DATETIME,
    FOREIGN KEY (stream_type_id) REFERENCES stream_types(id)
);
```

### Proposals Table
```sql
CREATE TABLE proposals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stream_url VARCHAR NOT NULL UNIQUE,
    name VARCHAR NOT NULL,
    website_url VARCHAR,
    stream_type_id INTEGER,
    is_secure BOOLEAN NOT NULL DEFAULT 1,
    country VARCHAR,
    description VARCHAR,
    image_url VARCHAR,
    FOREIGN KEY (stream_type_id) REFERENCES stream_types(id)
);
```

## API Endpoints

### Database Routes (`/`)

| Method | Endpoint | Description | Response |
|--------|----------|-------------|----------|
| GET | `/` | Homepage | HTML (Bootstrap UI) |
| GET | `/api/stats` | System statistics | `{"total_proposals": int, "total_sources": int, "total_stream_types": int}` |
| GET | `/api/stream-types` | All stream types | `[{"id": int, "name": str, "protocol": str, "format": str, "metadata_type": str}]` |

### Proposal Routes (`/proposal/`)

| Method | Endpoint | Description | Response |
|--------|----------|-------------|----------|
| GET | `/propose` | Proposal form | HTML |
| POST | `/propose` | Submit proposal | Redirect |
| GET | `/proposal/<id>` | Proposal details | HTML |
| POST | `/proposal/<id>/approve` | Approve proposal | Redirect |
| GET | `/api/proposals` | All proposals | `[{"id": int, "stream_url": str, ...}]` |
| GET | `/api/proposal/<id>/validate` | Validate proposal | `{"valid": bool, "issues": []}` |

### Radio Source Routes (`/source/`)

| Method | Endpoint | Description | Response |
|--------|----------|-------------|----------|
| GET | `/source/<id>` | Source details | HTML |
| GET | `/source/<id>/edit` | Edit source form | HTML |
| POST | `/source/<id>/edit` | Update source | Redirect |
| POST | `/source/<id>/delete` | Delete source | Redirect |
| GET | `/api/sources` | All sources | `[{"id": int, "name": str, ...}]` |
| GET | `/api/source/<id>` | Single source | `{"id": int, "name": str, ...}` |

## Data Transfer Objects (DTOs)

### Stream Analysis DTO
```python
from pydantic import BaseModel, ConfigDict

class StreamAnalysisDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    url: str
    is_valid: bool
    stream_type: Optional[StreamTypeDTO] = None
    metadata: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
```

### Stream Type DTO
```python
class StreamTypeDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    protocol: str  # HTTP, HTTPS, HLS
    format: str    # MP3, AAC, OGG
    metadata_type: str  # Icecast, Shoutcast, None
    display_name: str
```

### Validation DTO
```python
class ValidationResultDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    is_valid: bool
    issues: List[str] = []
    suggestions: List[str] = []
```

## Repository Pattern Implementation

### Repository Interface
All repositories implement a consistent interface:

```python
class BaseRepository:
    def find_by_id(self, id: int) -> Optional[T]:
        """Retrieve entity by primary key"""

    def find_all(self) -> List[T]:
        """Retrieve all entities"""

    def save(self, entity: T) -> T:
        """Insert or update entity"""

    def count(self) -> int:
        """Count total entities"""
```

### Repository Getter Functions
To avoid session management issues, repositories are accessed via getter functions:

```python
def get_radio_source_repo() -> RadioSourceRepository:
    from database import db
    return RadioSourceRepository(db.session)

def get_proposal_repo() -> ProposalRepository:
    from database import db
    return ProposalRepository(db.session)

def get_stream_type_repo() -> StreamTypeRepository:
    from database import db
    return StreamTypeRepository(db.session)
```

## Service Layer

### Stream Analysis Service
- Analyzes URLs to determine if they contain valid audio streams
- Classifies stream types (protocol, format, metadata)
- Extracts metadata from streams
- Validates stream accessibility and format

### Proposal Validation Service
- Validates proposal data completeness
- Checks for duplicate URLs
- Performs business rule validation
- Prepares proposals for approval

### Radio Source Service
- Manages radio source CRUD operations
- Handles source approval from proposals
- Maintains data integrity constraints

## Web Interface

### Bootstrap Integration
- Responsive design with Bootstrap 5.3.0
- Navigation bar with sections for different features
- Form styling and validation feedback
- Modal dialogs for confirmations

### Template Structure
```
templates/
├── index.html          # Homepage with overview
├── proposals.html      # List all proposals
├── proposal.html       # Single proposal view
├── sources.html        # List all sources
├── source_detail.html  # Single source view
├── edit_source.html    # Source editing form
└── database.html       # Database statistics view
```

### Static Assets
```
static/
├── css/
│   └── custom.css      # Custom styling
├── js/
│   └── app.js          # Frontend JavaScript
└── images/
    └── logo.png        # Application logo
```

## Testing Strategy

### Unit Tests
- Test individual service methods
- Validate DTO serialization/deserialization
- Test repository CRUD operations
- Mock external dependencies

### Integration Tests
- Test complete workflows (Spec 001 → 002 → 003)
- Validate API endpoint responses
- Test database operations end-to-end

### Test Structure
```
tests/
├── unit/
│   ├── test_stream_analysis_service.py
│   ├── test_proposal_validation_service.py
│   └── test_radio_source_service.py
└── integration/
    └── test_validate_and_add_workflow.py
```

## Deployment & Setup

### Local Development Setup

1. **Clone Repository**
   ```bash
   git clone <repository-url>
   cd RadioChWeb
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   # .venv\Scripts\activate   # Windows
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize Database**
   ```bash
   python init_db.py
   ```

5. **Run Application**
   ```bash
   python radioch_app.py
   ```

6. **Access Application**
   - Web Interface: http://127.0.0.1:5000
   - API Endpoints: http://127.0.0.1:5000/api/*

### Production Deployment

1. **Environment Variables**
   ```bash
   export FLASK_ENV=production
   export SECRET_KEY=your-secret-key-here
   ```

2. **Database Migration**
   - SQLite for development
   - MySQL/PostgreSQL for production (planned)

3. **WSGI Server**
   ```bash
   pip install gunicorn
   gunicorn -w 4 radioch_app:app
   ```

## Issues & Solutions

### Issue 1: Circular Import Between Models and App
**Problem**: Models imported `db` from `radioch_app`, causing circular dependency
**Solution**: Created separate `database.py` module with SQLAlchemy instance

### Issue 2: Pydantic Version Compatibility
**Problem**: Existing code used Pydantic v1 syntax, needed v2.12.0
**Solution**: Updated all DTOs to use `ConfigDict` instead of `Config`

### Issue 3: Database Schema Mismatches
**Problem**: SQLAlchemy models had columns not present in SQLite database
**Solution**: Manually added missing columns using SQLite ALTER TABLE commands

### Issue 4: Session Management in Repositories
**Problem**: Repository instances created outside app context lost database sessions
**Solution**: Implemented repository getter functions that create fresh repository instances with current session

### Issue 5: API Route Attribute Errors
**Problem**: Routes accessed non-existent model attributes (e.g., `st.name` instead of `st.display_name`)
**Solution**: Updated route code to use correct model attribute names

## Future Development

### Phase 2: Stream Analysis Integration
- Integrate Spec 003 stream analysis service
- Implement URL validation and classification
- Add real-time stream testing capabilities

### Phase 3: Proposal Workflow
- Complete Spec 002 proposal validation
- Implement approval/rejection workflow
- Add bulk proposal processing

### Phase 4: Advanced Features
- Playlist file support (.m3u, .pls)
- Stream quality analysis
- Geographic source mapping
- API rate limiting and caching

### Phase 5: Production Deployment
- Database migration to MySQL/PostgreSQL
- Docker containerization
- CI/CD pipeline setup
- Monitoring and logging

### Technical Improvements
- Comprehensive test coverage
- API documentation (Swagger/OpenAPI)
- Performance optimization
- Security hardening

---

**Document Version**: 1.0.0
**Last Updated**: 2025-11-29
**Project Status**: Core architecture complete, ready for feature integration