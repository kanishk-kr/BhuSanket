"""GIS routes — geospatial queries for map views."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func, cast, Float
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.auth import get_current_user
from app.models.user import User
from app.models.project import Project
from app.models.parcel import Parcel
from app.schemas import GeoProjectResponse

router = APIRouter(prefix="/geo", tags=["GIS"])


@router.get("/projects", response_model=list[GeoProjectResponse])
async def get_geo_projects(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    min_risk: float | None = None,
    state: str | None = None,
):
    """Get projects with geospatial data for map rendering."""
    query = select(Project)
    if min_risk is not None:
        query = query.where(Project.current_risk_score >= min_risk)
    if state:
        query = query.where(Project.state == state)

    result = await db.execute(query)
    projects = result.scalars().all()

    geo_projects = []
    for p in projects:
        geo_projects.append(GeoProjectResponse(
            id=p.id,
            name=p.name,
            risk_score=p.current_risk_score,
            status=p.status,
            lat=None,  # Computed from geometry in production
            lng=None,
            geometry_geojson=None,
        ))

    return geo_projects


@router.get("/parcels")
async def get_geo_parcels(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    project_id: str | None = None,
    blocking_only: bool = False,
):
    """Get parcels with geospatial data."""
    query = select(Parcel)
    if project_id:
        query = query.where(Parcel.project_id == project_id)
    if blocking_only:
        query = query.where(Parcel.is_blocking == True)

    result = await db.execute(query.limit(1000))
    parcels = result.scalars().all()

    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {
                    "id": str(p.id),
                    "ulpin": p.ulpin,
                    "survey_no": p.survey_no,
                    "status": p.acquisition_status,
                    "possession": p.possession_status,
                    "criticality": p.criticality_weight,
                    "is_blocking": p.is_blocking,
                    "area": p.area_hectares,
                },
                "geometry": None,  # PostGIS geometry → GeoJSON in production
            }
            for p in parcels
        ],
    }
