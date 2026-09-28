"""
Celery worker configuration for background tasks:
predictions, alerts, data ingestion, and scheduled jobs.
"""

from celery import Celery
from celery.schedules import crontab

from app.config import get_settings

settings = get_settings()

celery_app = Celery(
    "bhusanket",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Kolkata",
    enable_utc=True,
    task_routes={
        "app.tasks.predictions.*": {"queue": "predictions"},
        "app.tasks.alerts.*": {"queue": "alerts"},
        "app.tasks.*": {"queue": "default"},
    },
    beat_schedule={
        "refresh-predictions-hourly": {
            "task": "app.tasks.refresh_all_predictions",
            "schedule": crontab(minute=0),
        },
        "check-statutory-clocks": {
            "task": "app.tasks.check_statutory_clocks",
            "schedule": crontab(minute="*/15"),
        },
        "detect-data-staleness": {
            "task": "app.tasks.detect_data_staleness",
            "schedule": crontab(minute=0, hour="*/6"),
        },
    },
)


@celery_app.task(name="app.tasks.refresh_all_predictions")
def refresh_all_predictions():
    """Re-score all active projects."""
    pass  # Implemented with sync DB access in production


@celery_app.task(name="app.tasks.check_statutory_clocks")
def check_statutory_clocks():
    """Check all active statutory clocks and generate alerts."""
    pass


@celery_app.task(name="app.tasks.detect_data_staleness")
def detect_data_staleness():
    """Check data source freshness and flag stale feeds."""
    pass


@celery_app.task(name="app.tasks.score_project")
def score_project(project_id: str):
    """Score a single project (triggered by events)."""
    pass
