from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import sources

app = FastAPI(title="RadioChWeb API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sources.router)


@app.get("/health")
def health():
    return {"status": "ok"}
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes import sources

app = FastAPI(title="RadioChWeb API", version="0.1.0")

# CORS will be configured via env in Phase 2; allow all for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sources.router, prefix="/api/v1/sources", tags=["sources"])


@app.get("/api/v1/health")
def health():
    return {"status": "ok"}
