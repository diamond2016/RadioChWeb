![favicon](static/favicon.png)  **RadioChWeb**

*RadioChWeb* is a radio stream discovery and management web application built with Flask. It analyzes candidate streams (using ffmpeg and curl), stores analysis results, and provides a simple workflow to propose, review, and approve radio sources.

### Features
- Guest: search and listen to streams without signing in.
- Registered user: submit streams for analysis, view and update their submissions, and create "proposals" to add new radio sources.
- Admin: review proposals and approve or reject them; approved sources are added to the database.

### How it works
The core operation is "Analyze Stream". The app uses ffmpeg or curl to probe a stream and extract metadata (bitrate, codec, duration, etc.). Analysis results are persisted and drive acceptance decisions; validated streams become part of the stored radio catalog.

# RadioChWeb

![favicon](static/favicon.png)

RadioChWeb is a radio stream discovery and management web application built with Flask. It analyzes candidate streams (using ffmpeg and curl), stores analysis results, and provides a simple workflow to propose, review, and approve radio sources.

Key points
- Guest users can search and listen to streams.
- Registered users can submit streams for analysis and make proposals.
- Admins review proposals and approve or reject radio sources.

Installation (quick)
1. Clone:

```bash
git clone https://github.com/diamond2016/RadioChWeb.git
cd RadioChWeb
```

2. Create and activate venv (Unix/macOS):

```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. Install dependencies:

```bash
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
```

4. Initialize DB (migration helper):

```bash
cd migrate_db
python init_db.py
cd ..
```

5. Run the app (development):

```bash
FLASK_APP=app.py FLASK_ENV=development flask run
# or: python app.py
```

Testing

```bash
pytest -q
```

Release
- This repository is released under the Apache-2.0 license. See `LICENSE`.

Resources
- Architecture notes: `ARCHITECTURE.md`
- Web UI notes: `web-interface.md`
- Repo: https://github.com/diamond2016/RadioChWeb

If you need a developer quickstart or CI setup, I can add a `.github/workflows` example next.
