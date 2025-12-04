## Feature: Listen logging (fast counter + detailed events)

### Goal

- Record user plays of streams to enable metrics and basic analytics.
- Two-tier logging:
  - Fast counter on `radio_source.listen_count` (increment for each play).
  - `listen_event` table with per-play details (timestamp, anonymized IP, user-agent, referrer, optional duration/extra).

### Design overview

- Add DB migration `V7_0__add_listen_logging.sql`.
- Add `ListenRepository` to encapsulate DB inserts & counter increments.
- Log from the listen route asynchronously (daemon thread) to avoid blocking page render.
- Anonymize IPs (salted hash) to protect privacy.
- Provide simple unit tests and route test skeleton (background thread tests may use a short sleep or mock `ListenRepository`).
- Optional future improvements: queue-based logging (Redis/Celery), aggregation jobs, retention policy.

### Migration (create file)

```sql
-- Adds listen_count column and listen_event table for logging plays
ALTER TABLE radio_source ADD COLUMN listen_count INTEGER DEFAULT 0;

CREATE TABLE IF NOT EXISTS listen_event (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id INTEGER NOT NULL,
    occurred_at TEXT NOT NULL, -- ISO8601 UTC
    ip TEXT,                   -- anonymized (hashed) IP
    user_agent TEXT,
    referrer TEXT,
    duration_seconds INTEGER,
    extra TEXT,                -- JSON string (nullable)
    FOREIGN KEY (source_id) REFERENCES radio_source(id)
);

CREATE INDEX IF NOT EXISTS idx_listen_event_source ON listen_event(source_id);
CREATE INDEX IF NOT EXISTS idx_listen_event_time ON listen_event(occurred_at);
```

### Repository helper

```python
from datetime import datetime
import json
from database import db

class ListenRepository:
    def __init__(self, session=None):
        self.session = session or db.session

    def insert_event(self, source_id: int, ip: str | None, user_agent: str | None,
                     referrer: str | None, duration_seconds: int | None = None, extra: dict | None = None):
        now = datetime.utcnow().isoformat()
        sql = """
        INSERT INTO listen_event (source_id, occurred_at, ip, user_agent, referrer, duration_seconds, extra)
        VALUES (:source_id, :occurred_at, :ip, :user_agent, :referrer, :duration_seconds, :extra)
        """
        self.session.execute(sql, {
            'source_id': source_id,
            'occurred_at': now,
            'ip': ip,
            'user_agent': user_agent,
            'referrer': referrer,
            'duration_seconds': duration_seconds,
            'extra': json.dumps(extra) if extra else None
        })
        self.session.commit()

    def increment_counter(self, source_id: int, amount: int = 1):
        sql = "UPDATE radio_source SET listen_count = COALESCE(listen_count,0) + :amount WHERE id = :id"
        self.session.execute(sql, {'amount': amount, 'id': source_id})
        self.session.commit()
```

### Route changes (log when player route is opened)

Approach: Spawn a daemon thread that calls `ListenRepository` to insert event and increment counter. This keeps the UI fast and is simple for low-to-moderate traffic.

```python
from flask import Blueprint, render_template, abort, request
from model.repository.radio_source_repository import RadioSourceRepository
from model.repository.listen_repository import ListenRepository
import threading
import hashlib
import os

listen_bp = Blueprint('listen', __name__, url_prefix='/listen')

def anonymize_ip(ip: str) -> str:
    # non-reversible salted hash for privacy
    salt = os.environ.get('LISTEN_LOG_SALT', 'change-me')
    return hashlib.sha256((ip or '').encode('utf-8') + salt.encode('utf-8')).hexdigest()

def _log_listen_async(source_id, req):
    try:
        repo = ListenRepository()
        ip = req.headers.get('X-Forwarded-For', req.remote_addr)
        ip_hashed = anonymize_ip(ip)
        ua = req.headers.get('User-Agent')
        ref = req.headers.get('Referer')
        repo.insert_event(source_id=source_id, ip=ip_hashed, user_agent=ua, referrer=ref, duration_seconds=None)
        repo.increment_counter(source_id)
    except Exception:
        # swallow exceptions to avoid affecting user experience
        pass

@listen_bp.route("/<int:source_id>")
def player(source_id: int):
    radio_repo = RadioSourceRepository()
    source = radio_repo.find_by_id(source_id)
    if not source:
        abort(404)
    # spawn background logger
    threading.Thread(target=_log_listen_async, args=(source_id, request), daemon=True).start()
    return render_template('listen_player.html', source=source)
```

### Template: listen_player.html (no changes required if you already have it)

Ensure `listen_player.html` is a small page and that the Listen link opens `/listen/<id>`.

### Testing

#### Unit tests for ListenRepository:

- `tests/unit/test_listen_logging.py`

```python
import pytest
import time
from model.repository.listen_repository import ListenRepository
from model.repository.radio_source_repository import RadioSourceRepository

def test_listen_route_logs_and_increments(client, test_db):
    # create radio_source row and get id (use repo)
    rr = RadioSourceRepository()
    source = rr.create_or_save_some_fixture(...)  # adapt to your test helpers
    resp = client.get(f'/listen/{source.id}')
    assert resp.status_code == 200
    # allow background thread to run
    time.sleep(0.1)
    lr = ListenRepository()
    cur = test_db.execute("SELECT COUNT(*) FROM listen_event WHERE source_id = ?", (source.id,))
    assert cur.fetchone()[0] >= 1
    cur = test_db.execute("SELECT listen_count FROM radio_source WHERE id = ?", (source.id,))
    assert cur.fetchone()[0] >= 1
```

### Privacy & compliance

- IPs: Store salted hash (non-reversible). Use env var `LISTEN_LOG_SALT`; rotate carefully (rotating salt breaks correlation).
- Limit retention: Plan for periodic aggregation and deletion of old `listen_event` rows (e.g., keep events 90 days).
- GDPR: Document purpose, retention, and anonymization in repo docs.

### Operational notes

- For low traffic, daemon thread is fine. For high volume, switch to a queue (Redis + worker) or batch writes to avoid DB contention.
- Monitor `listen_event` growth, add partition/archival if needed.
- Indexes: Created on `source_id` and `occurred_at`.
- Backups: Include `listen_event` in DB backups or separate storage.

### Migration & rollout steps

- Add migration file `V7_0__add_listen_logging.sql`, run migrations on dev.
- Deploy route/listen changes to staging, smoke-test player page.
- Monitor DB inserts, CPU, and latency.
- If OK, deploy to production and enable `LISTEN_LOG_SALT` env var.

### PR contents (suggested commit files)

- `migrate_db/migrations/V7_0__add_listen_logging.sql`
- `model/repository/listen_repository.py`
- `listen_route.py` (or modification to existing listen route)
- `tests/unit/test_listen_logging.py`
- `docs/specs/005-listen-logging/README.md` (this document)

### PR checklist

- Migration file added and validated locally.
- New repository file present and imported from route.
- Listen route registered in app (`app.py` or blueprint registration).
- Unit tests added and passing locally.
- ENV note added to docs about `LISTEN_LOG_SALT`.
- Performance considerations documented.
- Privacy & retention documented.

### Deployment note

Set env var `LISTEN_LOG_SALT` in production before enabling logging. Monitor DB size and performance after rollout.


