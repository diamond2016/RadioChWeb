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









### 🔧 Technology Stack

#### Core Technologies
- **Python 3.14+**: Primary programming language
- **Flask 2.3.2**: Web framework for API endpoints
- **SQLAlchemy 2.0.43**: ORM and database abstraction
- **Textual 6.5.0**: Terminal user interface framework
- **Pydantic 2.12.0**: Data validation and serialization

#### Development Tools
- **pytest 8.3.4**: Testing framework with asyncio support
- **pytest-asyncio 1.3.0**: Async testing utilities
- **pytest-cov 4.0.0**: Code coverage reporting
- **PyWay 0.3.32**: Database migration tool

#### External Dependencies
- **ffmpeg**: Audio stream analysis and metadata extraction
- **curl**: HTTP header inspection and validation

## Development State

### ✅ **Completed Features**

#### **Spec 003: Analyze and Classify Stream** 🎯
- **Status**: ✅ **PRODUCTION READY**
- **Coverage**: 59% test coverage, 10/10 tests passing
- **Features**:
  - Dual validation (curl headers + ffmpeg analysis)
  - 14 predefined StreamType classifications
  - Security detection (HTTP/HTTPS)
  - Timeout handling (30s max, configurable)
  - Comprehensive error reporting
  - Textual TUI integration with real-time feedback

#### **Spec 002: Validate and Add Radio Source** ✅
- **Status**: ✅ **PRODUCTION READY**
- **Coverage**: 44 tests passing (unit + integration)
- **Features**:
  - ProposalValidationService with full validation logic
  - RadioSourceService for saving/rejecting proposals
  - Duplicate stream URL detection
  - Security warnings for HTTP streams
  - Required field validation (streamUrl, name, websiteUrl)
  - Full Textual TUI integration with proposal management
  - DataTable views for proposals, stream types, radio sources
  - Modal edit screen with save/reject functionality
  - Database migration integration

#### **Database Layer** 🗄️
- **Status**: ✅ **FULLY IMPLEMENTED**
- **Features**:
  - PyWay migration system (replacing manual scripts)
  - Complete schema with indexes and foreign keys
  - Repository pattern implementation
  - Session management with proper cleanup

#### **Testing Infrastructure** 🧪
- **Status**: ✅ **ESTABLISHED**
- **Features**:
  - pytest with asyncio support
  - Unit test coverage for core services
  - Integration tests for end-to-end workflows
  - Test configuration and fixtures
  - Code coverage reporting

### 🚧 **In Progress**

#### **Spec 001: Discover Radio Source** 🔍
- **Status**: 📝 **SPECIFIED** (implementation pending)
- **Scope**: URL input → scraping → validation → proposal creation
- **Priority**: P1 (core functionality)

#### **Textual TUI Enhancement** 💻
- **Status**: ✅ **PRODUCTION READY** (for Spec 002 & 003)
- **Completed**: 
  - Stream analysis tab with real functionality
  - Validate & Add tab with proposal management
  - Database management tabs with migration support
- **Pending**: Spec 001 discovery tab

### 📋 **Planned Features**

#### **API Layer** 🌐
- Flask REST endpoints for all services
- OpenAPI/Swagger documentation
- CLI tools for API interaction

#### **Advanced Features** ⚡
- Concurrent stream analysis
- Playlist parsing and expansion
- Batch processing capabilities
- Export/import functionality

#### **Quality Assurance** 🔍
- Integration test suite
- Performance benchmarking
- Security auditing
- Documentation completion

## Development Workflow

### 🏃 **Current Workflow**
1. **Specification**: Create detailed spec.md with user stories
2. **Planning**: Generate implementation plan.md with tasks
3. **Implementation**: TDD approach with comprehensive testing
4. **Integration**: Textual TUI integration and validation
5. **Migration**: PyWay database schema updates

### 🧪 **Testing Strategy**
- **Unit Tests**: Service layer business logic
- **Integration Tests**: End-to-end workflows (planned)
- **TUI Tests**: Interface validation (planned)
- **Coverage Target**: >80% overall coverage

### 🚀 **Deployment**
- **Environment**: Python virtual environment
- **Database**: SQLite (development), PostgreSQL (production planned)
- **Dependencies**: requirements.txt with pinned versions
- **Migration**: Automated PyWay migrations

## Key Design Decisions

### **Architecture Principles**
- **Backend-First**: Core logic developed before UI
- **API-First**: All services exposed via REST APIs
- **Service-Oriented**: Clear separation of concerns
- **Test-Driven**: Comprehensive test coverage mandatory

### **Technology Choices**
- **Textual over CLI**: Rich terminal UI for better UX
- **PyWay over Manual**: Automated migration management
- **pytest over unittest**: Modern testing framework
- **Pydantic v2**: Latest data validation standard

### **Data Design**
- **Normalized Schema**: Proper relational design
- **Lookup Tables**: Predefined stream types for consistency
- **Proposal Pattern**: Two-phase validation workflow
- **Comprehensive Indexing**: Performance optimization

## Getting Started

### **Prerequisites**
```bash
# Python 3.14+
python3 --version

# External tools
which ffmpeg  # Audio analysis
which curl    # HTTP validation
```

### **Setup**
```bash
# Clone and setup
cd RadioCh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Initialize database
python migrate.py

# Run tests
pytest -v

# Launch application
python radioch_app.py
```

### **Development**
```bash
# Run specific tests
pytest tests/unit/test_stream_analysis_service.py -v

# Check coverage
pytest --cov=src --cov-report=html

# Database operations
python migrate.py status
python migrate.py migrate
```

## Future Roadmap

### **Phase 1: Complete Core Specs** (Current)
- Implement Spec 001 (Discovery)
- Implement Spec 002 (Validation)
- Enhance TUI with full workflow

### **Phase 2: API & Integration**
- Complete Flask API layer
- Add CLI tools
- Implement batch processing

### **Phase 3: Advanced Features**
- Web interface (React/Vue)
- Mobile applications
- Advanced analytics
- Multi-format support

### **Phase 4: Production**
- PostgreSQL migration
- Docker containerization
- CI/CD pipeline
- Performance optimization

---

**Last Updated**: November 25, 2025
**Python Version**: 3.12+
**Test Coverage**: 44 tests passing (unit + integration)
**Status**: Active Development - Spec 002 Complete
