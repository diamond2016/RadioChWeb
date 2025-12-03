# Copilot coding agent instructions for RadioChWeb

Purpose
- Give a coding agent a compact, high-value orientation so PRs it opens are more likely to build, test, and behave correctly on first try.
- Trust these instructions as the primary source of build/run/test/lint knowledge for this repo. Only perform a codebase search if something below is missing or proven incorrect.

High-level summary
- What this repo is: RadioChWeb is a small Flask-based web application (server-side Python + HTML templates) that provides a web interface for radio channel management / display (see web-interface.md and ARCHITECTURE.md for domain details).
- Languages & size: Primarily Python (core app) and HTML (templates). Language breakdown from the repository metadata: Python and HTML dominate.
- Key files at the repo root:
  - .gitignore
  - .vscode/
  - ARCHITECTURE.md
  - README.md
  - app.py (Flask app entry)
  - database.py (DB initialization/access)
  - migrate_db/ (migration scripts)
  - model/ (data models)
  - route/ (Flask routes / controllers)
  - service/ (application business logic)
  - templates/ (Jinja2 HTML templates)
  - specs/ (specifications)
  - tests/ (pytest tests)
  - requirements.txt
  - web-interface.md

Build & validation (what to always do, step-by-step)
- Overview: This is a plain Python project with pinned packages in requirements.txt. Always create an isolated virtual environment and install pinned requirements before any build/test/run work.
- Recommended Python: 3.10+ (3.11 recommended). If agent detects a different interpreter, prefer Python 3.10+.
- Always do these exact steps before running, testing, or making changes:
  1. Clone the repo and cd into it.
  2. Create and activate a virtual environment:
     - Unix/macOS:
       - python3 -m venv .venv
       - source .venv/bin/activate
     - Windows (PowerShell):
       - python -m venv .venv
       - .\.venv\Scripts\Activate.ps1
  3. Upgrade pip and install pinned deps:
     - python -m pip install --upgrade pip setuptools wheel
     - python -m pip install -r requirements.txt
     - NOTE: requirements.txt pins Flask and related libs — always use it exactly (do not unconstrained-upgrade unless debugging).
  4. Install any developer/test-only tools into the same venv (pytest is in requirements.txt).
- Run the app locally:
  - FLASK_APP=app.py FLASK_ENV=development flask run
  - Windows (PowerShell): $env:FLASK_APP="app.py"; $env:FLASK_ENV="development"; flask run
  - If flask CLI fails, try: python -m flask run (with FLASK_APP set).
- Run tests:
  - pytest -q
  - If collect fails, ensure venv activated and packages installed.
- Lint / formatting:
  - There is no enforced linter config in the root. If introducing style tooling, add config files (e.g., pyproject.toml, .flake8). Until then, format with black locally if desired.
- Database:
  - The codebase contains database.py and a migrate_db/ directory. By default run/test may use a local SQLite DB; inspect database.py to confirm connection string and env var names.
  - If tests require a DB, run tests after installing requirements and ensure the test runner provisions any test DBs (look for fixtures in tests/).
- Clean and rebuild:
  - To clean: deactivate venv, remove .venv, and remove __pycache__ directories.
  - Re-create venv and reinstall to reproduce clean environment.
- Known package versions (from requirements.txt; install exactly these):
  - Flask==3.0.0
  - Flask-SQLAlchemy==3.1.1
  - pytest==8.0.0
  - pytest-cov==4.1.0
  - pydantic==2.12.0
  - pyway==0.3.32
  - Flask_WTF==1.2.1

Troubleshooting & observed pitfalls (what to try first)
- If dependency install fails:
  - Upgrade pip and wheel: python -m pip install --upgrade pip setuptools wheel
  - Recreate venv from scratch.
- If Flask CLI errors about FLASK_APP or import errors:
  - Ensure you set FLASK_APP=app.py and run from repo root.
  - Check PYTHONPATH if imports are relative; running python -m flask run from project root usually resolves path issues.
- If tests fail nondeterministically:
  - Re-run pytest with -k to isolate failing tests.
  - Ensure no leftover state/db files remain from prior runs.
- If a CI problem is reported in a PR, replicate locally by following the "always do these exact steps" sequence.

Project layout and where to make changes
- Main entry: app.py — contains Flask application factory or app instance and top-level route registrations. Small changes to routing/handlers typically go here or under route/.
- Database concerns: database.py and migrate_db/ — changes touching persistent state, migrations, or models require careful consideration and test updates.
- Models: model/ — domain model classes and schemas.
- Business logic: service/ — put core logic here and keep route handlers thin (preferred isolation for testing).
- Templates: templates/ — Jinja2 HTML views; front-end/client changes go here (HTML/CSS).
- Tests: tests/ — unit and functional tests. Add/modify tests to cover changes; run pytest locally and include them in PRs.
- Architecture and interface docs: ARCHITECTURE.md and web-interface.md — read these before implementing cross-cutting changes.

Checks and CI
- I did not find an active GitHub Actions workflow in the root/.github/workflows in the repository snapshot. Assume no enforced CI in the repo; therefore local validation is required:
  - Run pip install -r requirements.txt
  - Run pytest -q
  - Run the Flask app locally and exercise key routes (manual smoke test).
- If you add CI or workflows, mirror the local steps above in the workflow YAML to ensure CI matches local runs.

What to include in a change/PR to avoid rework
- Always run tests; include updated/added tests for behavior changes.
- If you modify DB schemas or models:
  - Add migration script(s) into migrate_db/ if the project uses migrations.
  - Document any required manual migration steps in the PR description.
- For runtime-sensitive changes, include exact repro steps and expected output in the PR.
- Provide a short local validation checklist in the PR body (commands to run and expected results).

Repository artifacts (quick inventory)
- requirements.txt (pinned deps — see above).
- app.py — Flask app entry point (start here for runtime changes).
- database.py — DB init/connection helper.
- ARCHITECTURE.md — larger design doc — read before broad changes.
- web-interface.md — domain-specific UI/UX notes.
- Directories: model/, route/, service/, templates/, tests/, migrate_db/, specs/
- README.md — small readme (open it to see repository-specific startup notes if any).

Agent behavior rules (how you should operate here)
- Trust this file as the first source of truth for common commands and environment setup.
- Always run the "always do" sequence (venv creation, pip install -r requirements.txt, tests) before proposing code that changes runtime behavior.
- Only perform repository-wide searches if an instruction here is incomplete or a command fails in a way not accounted for.
- When opening a PR:
  - Run pytest locally and include test results in the PR summary.
  - Describe environment (Python version, OS) you used to validate.
  - If you changed dependencies, include a reproduction of pip freeze and the rationale.

If something here is out-of-date
- Consult ARCHITECTURE.md and web-interface.md for authoritative domain details and update this file via a small PR if you find inaccuracies.
- If a command fails, perform a focused code search for the failing module/file to gather corrective steps and update these instructions.

End of instructions.
