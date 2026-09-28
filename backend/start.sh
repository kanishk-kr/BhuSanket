#!/bin/bash
# start.sh - Run API, Celery Worker, and Celery Beat in a single container for free tier hosting

# Run migrations
alembic upgrade head

# Start Celery Beat in the background
celery -A app.worker beat --loglevel=info &

# Start Celery Worker in the background
celery -A app.worker worker --loglevel=info --concurrency=2 &

# Start FastAPI application in the foreground
# Render dynamically assigns a port via the $PORT environment variable
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
