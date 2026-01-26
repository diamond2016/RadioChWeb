import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes import stream_types, radio_sources, health

# create FastAPI app
app = FastAPI(title="RadioChWeb API", version="0.1.0", 
              openapi_tags=[ {"name": "sources", "description": "Radio sources read-only API"}, 
                             {"name": "health", "description": "Health check and diagnostics"},])


# CORS will be configured via env in Phase 2; allow all for local development
ALLOWED_ORIGINS: list[str] = os.getenv("CORS_ORIGINS", "*").split(",")
app.add_middleware(
    middleware_class=CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# register router
app.include_router(stream_types.router, prefix="/api/v1/stream_types") 
app.include_router(radio_sources.router, prefix="/api/v1/sources") 
app.include_router(health.router, prefix="/api/v1")

