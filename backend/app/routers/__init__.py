"""API routers package."""

from app.routers.auth import router as auth_router
from app.routers.projects import router as projects_router
from app.routers.events import router as events_router
from app.routers.alerts import router as alerts_router
from app.routers.interventions import router as interventions_router
from app.routers.governance import router as governance_router
from app.routers.geo import router as geo_router
from app.routers.dashboard import router as dashboard_router

__all__ = [
    "auth_router",
    "projects_router",
    "events_router",
    "alerts_router",
    "interventions_router",
    "governance_router",
    "geo_router",
    "dashboard_router",
]
