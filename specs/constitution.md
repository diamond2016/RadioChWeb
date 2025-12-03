# RadioChWeb (RadioChannelWeb) Constitution

## Core Principles

### I. Architecture
The application logic resides in the "backend" section, which is primarily composed of services.

### II. API-First
All services are exposed via APIs. This is the primary method of interaction.

### III. Decoupled Frontend and Backend
The backend and frontend are not coupled. They are developed and deployed as separate entities.

### IV. Interface
The application's user interface will be a web interface. It will exploit apis forr business logic.

### V. Test-Driven Development
No feature is implemented without a corresponding set of failing tests that are written first. All code must pass these tests before being merged.

## Technical Stack & Standards

*   The backend application MUST use the Flask framework and SQLAlchemy for persistence
*   Persistence is made with a generic SQL database, The database chosen is SQLite.
*   Core services SHOULD be exposed with JSON payloads whenever possible.
*   The backend language MUST be Python 3.13 or a later version.
*   All Python development MUST be done within a virtual environment (`venv`).
*   Testing MUST be done using assertion test cases

## Governance

*   This constitution is the single source of truth for project principles and standards. It supersedes any other informal practices.
*   Any proposed changes to this constitution must be reviewed and approved by the project owner.
*   All code contributions and architectural decisions must be compliant with the principles outlined in this document.

**Version**: 1.0.0 | **Ratified**: 2025-11-29 | **Last Amended**: 2025-11-29
