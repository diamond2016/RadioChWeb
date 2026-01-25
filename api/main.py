import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes import sources, health

# create FastAPI app
app = FastAPI(title="RadioChWeb API", version="0.1.0", 
              openapi_tags=[ {"name": "sources", "description": "Radio sources read-only API"}, 
                             {"name": "health", "description": "Health check and diagnostics"},])

# hooks to be moved in future
@app.on_event("startup") 
def startup_event(): print("API starting…") 

@app.on_event("shutdown") 
def shutdown_event(): print("API shutting down…")

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
app.include_router(sources.router, prefix="/api/v1/sources") 
app.include_router(health.router, prefix="/api/v1")

