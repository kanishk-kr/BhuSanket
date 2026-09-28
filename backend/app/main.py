"""
BhuSanket — Main FastAPI application.
Land Acquisition Intelligence Platform for Early Detection of Delays.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.config import get_settings
from app.database import init_db
from app.routers import (
    auth_router,
    projects_router,
    events_router,
    alerts_router,
    interventions_router,
    governance_router,
    geo_router,
    dashboard_router,
)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle: startup and shutdown hooks."""
    # Startup
    await init_db()
    yield
    # Shutdown (cleanup if needed)


app = FastAPI(
    title="BhuSanket API",
    description=(
        "Land Acquisition Intelligence Platform — Predictive intelligence overlay "
        "for early detection of delays in land acquisition projects. "
        "Ministry of Rural Development, Department of Land Resources."
    ),
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus metrics
Instrumentator().instrument(app).expose(app, include_in_schema=False)

# Mount routers
prefix = settings.api_prefix
app.include_router(auth_router, prefix=prefix)
app.include_router(projects_router, prefix=prefix)
app.include_router(events_router, prefix=prefix)
app.include_router(alerts_router, prefix=prefix)
app.include_router(interventions_router, prefix=prefix)
app.include_router(governance_router, prefix=prefix)
app.include_router(geo_router, prefix=prefix)
app.include_router(dashboard_router, prefix=prefix)


from app.seed.seed_db import run_seed

@app.get("/seed")
async def seed_database():
    try:
        await run_seed()
        return {"status": "success", "message": "Database seeded successfully!"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "bhusanket-api", "version": "0.1.0"}


@app.get("/")
async def root():
    return {
        "service": "BhuSanket API",
        "version": "0.1.0",
        "docs": "/docs",
        "description": "Land Acquisition Intelligence Platform",
    }
