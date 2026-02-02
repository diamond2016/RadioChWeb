# Running the API from the `api/` folder

If you run `uvicorn` from inside the `api/` directory, you need to ensure the repository root is on `PYTHONPATH` so `import api...` works.

Options:

- From `api/` directly:

```bash
PYTHONPATH=.. uvicorn main:app --reload --port 5001
```

- Or use the included helper script (from `api/`):

```bash
./run_uvicorn.sh
```

Notes:
- The helper script sets `PYTHONPATH` to the repo root and then execs `uvicorn`.
- Alternatively, run from the repository root with `uvicorn api.main:app`.

## Running from a network share (publish workflow)

If you publish `api/` to a network-mounted path (for example `/home/riccardo/Dati_server/radiochweb`), follow this recommended workflow. The scripts support passing the destination as an argument or via the `SHARE_PATH` environment variable.

1. From your development machine, sync `api/` to the share (example using the configured share path):

```bash
SHARE_PATH=/home/riccardo/Dati_server/radiochweb ./scripts/deploy_to_share.sh
```

2. On the target machine (where the share is mounted), create an isolated venv and install dependencies (defaults to `/opt/radiochweb_venv`):

```bash
SHARE_PATH=/home/riccardo/Dati_server/radiochweb sudo ./scripts/remote_setup.sh
```

3. Run `uvicorn` from the target using the created venv (example):

```bash
/opt/radiochweb_venv/bin/uvicorn api.main:app --host 0.0.0.0 --port 5001
```

4. Optionally, use the example systemd unit in `deploy/api.service` as a template to run the API as a service. Edit `WorkingDirectory` and `ExecStart` to match your mount point and venv.

Notes and caveats:
- Do not copy an active virtualenv from one host to another — instead create a venv on the target with `remote_setup.sh` so binary wheels and interpreter paths are correct.
- Ensure the target Python version is compatible with your dependencies (Python 3.10+ recommended).
- If the API uses local file-based DBs (SQLite) consider where the DB file should live; network-mounted SQLite files may be undesirable for concurrent access.
