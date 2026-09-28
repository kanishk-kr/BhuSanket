# BhuSanket

A Land Acquisition Intelligence Platform for Early Detection of Delays.

**BhuSanket** is an intelligence layer that sits on top of existing land, payment, court, and project systems. It builds a continuously updated Land Acquisition Intelligence Graph and provides predictive insights (Will it be delayed? When? Why? What should we do? What will it affect?) to help land acquisition officers proactively manage risks.

## Features
- **Statutory Deadline Engine**: Clocks legal limits in land acquisition acts.
- **Predictive Engine**: Early detection of project delays via AI models.
- **Explainability**: Understand exactly *why* a project is at risk through evidence-backed drivers.
- **GIS Intelligence**: Understand how spatial bottlenecks prevent workfront readiness.
- **Scenario Simulator**: Simulate administrative interventions to reduce risk mathematically.
- **Audit Logging**: Immutable hash-chained audit logs for model transparency.

## Tech Stack
- **Frontend**: Next.js (App Router), Tailwind CSS, Lucide Icons, MapLibre
- **Backend**: Python, FastAPI, SQLAlchemy, Alembic, Celery
- **Database/Cache**: PostgreSQL (PostGIS enabled), Redis
- **Infrastructure**: Docker & Docker Compose, Nginx

## Quickstart

Run the full stack locally with Docker Compose:

```bash
docker-compose up --build -d
```
Then visit `http://localhost:3000` to view the application!
