"""
Database seeder — populates the database with synthetic data, legal templates,
roles, and demo users for the MVP.
"""

import asyncio
import uuid
import json
from datetime import date, datetime, timedelta, timezone

from app.database import engine, async_session_factory, init_db
from app.models.user import User, Role
from app.models.project import Project, Package, Milestone, Dependency
from app.models.stage import Stage
from app.models.parcel import Parcel
from app.models.legal import (
    LegalProcessTemplate, TemplateStage, StatutoryClockDefinition,
    StatutoryClockInstance,
)
from app.models.alert import Alert
from app.models.prediction import ModelVersion, DataSource
from app.models.intervention import AllowedAction
from app.auth import hash_password
from app.seed.synthetic_generator import (
    generate_synthetic_dataset,
    generate_parcels_for_project,
    generate_alerts_for_project,
    STAGE_SEQUENCE,
)
from app.engine.statutory_deadline import RFCTLARR_2013_CLOCKS


async def seed_roles(session):
    """Create RBAC roles per spec Section 11.3."""
    roles_data = [
        {"name": "admin", "description": "System administrator"},
        {"name": "ministry", "description": "Ministry/Policy level"},
        {"name": "state_nodal", "description": "State nodal officer"},
        {"name": "collector", "description": "District Collector"},
        {"name": "project_manager", "description": "Project manager (requiring body)"},
        {"name": "field_officer", "description": "Field officer"},
        {"name": "legal_officer", "description": "Legal officer"},
        {"name": "rr_officer", "description": "R&R officer"},
        {"name": "data_steward", "description": "Data steward"},
        {"name": "model_governor", "description": "Model governor/auditor"},
    ]
    roles = {}
    for rd in roles_data:
        role = Role(name=rd["name"], description=rd["description"])
        session.add(role)
        roles[rd["name"]] = role
    await session.flush()
    return roles


async def seed_users(session, roles):
    """Create demo users."""
    users_data = [
        {"email": "admin@bhusanket.gov.in", "name": "System Admin", "role": "admin", "password": "admin123"},
        {"email": "collector@bhusanket.gov.in", "name": "Dr. Priya Sharma", "role": "collector", "password": "demo123", "district": "Jaipur", "state": "Rajasthan"},
        {"email": "ministry@bhusanket.gov.in", "name": "Shri Rajesh Kumar", "role": "ministry", "password": "demo123"},
        {"email": "pm@bhusanket.gov.in", "name": "Anil Verma", "role": "project_manager", "password": "demo123", "state": "Maharashtra"},
        {"email": "legal@bhusanket.gov.in", "name": "Adv. Meera Nair", "role": "legal_officer", "password": "demo123"},
    ]
    for ud in users_data:
        user = User(
            email=ud["email"],
            hashed_password=hash_password(ud["password"]),
            full_name=ud["name"],
            role_id=roles[ud["role"]].id,
            jurisdiction=ud.get("district") or ud.get("state"),
            state=ud.get("state"),
            district=ud.get("district"),
        )
        session.add(user)
    await session.flush()


async def seed_legal_template(session):
    """Create the RFCTLARR 2013 legal process template."""
    template = LegalProcessTemplate(
        name="Right to Fair Compensation and Transparency in Land Acquisition, Rehabilitation and Resettlement Act, 2013",
        code="RFCTLARR_2013",
        version="1.0",
        jurisdiction="India (Central)",
        legal_regime="RFCTLARR 2013",
        description="Primary land acquisition law; Act 30 of 2013",
        effective_from=date(2014, 1, 1),
        legal_review_status="reviewed",
        reviewed_by="Legal Team",
        reviewed_on=date(2026, 9, 1),
    )
    session.add(template)
    await session.flush()

    # Template stages
    for i, stage_def in enumerate(STAGE_SEQUENCE):
        ts = TemplateStage(
            template_id=template.id,
            name=stage_def["name"],
            code=stage_def["code"],
            sequence_order=i,
            expected_duration_days=stage_def["base_duration"][1],
            silence_threshold_days=30,
        )
        session.add(ts)

    # Statutory clocks
    for clock_def in RFCTLARR_2013_CLOCKS:
        clock = StatutoryClockDefinition(
            template_id=template.id,
            clock_code=clock_def["clock_code"],
            section_reference=clock_def["section_reference"],
            description=clock_def["description"],
            trigger_event=clock_def["trigger_event"],
            end_event=clock_def["end_event"],
            duration_days=clock_def["duration_days"],
            expiry_consequence=clock_def["expiry_consequence"],
            consequence_description=clock_def.get("consequence_description"),
            pause_rules=clock_def.get("pause_rules"),
            effective_from=date(2014, 1, 1),
            legal_review_status="reviewed",
        )
        session.add(clock)

    await session.flush()
    return template


async def seed_allowed_actions(session):
    """Create allow-listed administrative actions."""
    from app.engine.scenario import ALLOWED_ACTIONS
    for code, details in ALLOWED_ACTIONS.items():
        action = AllowedAction(
            code=code,
            name=details["name"],
            category=details["category"],
            typical_duration_days=14,
        )
        session.add(action)
    await session.flush()


async def seed_data_sources(session):
    """Create data source records."""
    sources = [
        ("State Land Stack (DILRMP 3.0)", "land_stack", "mock"),
        ("Bhoomi Rashi (MoRTH)", "acquisition_status", "mock"),
        ("PFMS", "payment_system", "mock"),
        ("NJDG / Court Data", "court_data", "mock"),
        ("PARIVESH", "approval_tracker", "mock"),
        ("Requiring Body Feed", "project_data", "mock"),
    ]
    for name, stype, health in sources:
        ds = DataSource(
            name=name,
            source_type=stype,
            health_status=health,
            last_sync=datetime.now(timezone.utc) - timedelta(hours=6),
        )
        session.add(ds)
    await session.flush()


async def seed_model_version(session):
    """Create initial model version."""
    model = ModelVersion(
        model_type="discrete_time_hazard",
        version="0.1.0-synthetic",
        training_window_start=date(2020, 1, 1),
        training_window_end=date(2026, 9, 1),
        metrics_json={
            "roc_auc": 0.847,
            "pr_auc": 0.723,
            "brier_score": 0.142,
            "calibration_error": 0.038,
            "c_index": 0.812,
            "coverage_90": 0.891,
        },
        is_active=True,
        approved_by="Model Governor",
        approved_on=date(2026, 9, 15),
        status="active",
    )
    session.add(model)
    await session.flush()


async def seed_projects(session, template, n_projects=100):
    """Seed synthetic projects with stages, parcels, and alerts."""
    dataset = generate_synthetic_dataset(n_projects)

    for proj_data in dataset[:n_projects]:
        project = Project(
            name=proj_data["name"],
            code=proj_data["code"],
            requiring_body_id=proj_data["requiring_body_id"],
            template_id=template.id,
            jurisdiction=proj_data["jurisdiction"],
            state=proj_data["state"],
            district=proj_data["district"],
            sector=proj_data["sector"],
            budget=proj_data["budget"],
            status=proj_data["status"],
            total_parcels=proj_data["total_parcels"],
            total_area_hectares=proj_data["total_area_hectares"],
            land_acquired_pct=proj_data["land_acquired_pct"],
            construction_enabling_pct=proj_data["construction_enabling_pct"],
            current_risk_score=proj_data["current_risk_score"],
            risk_momentum=proj_data["risk_momentum"],
            risk_momentum_class=proj_data["risk_momentum_class"],
            model_confidence=proj_data["model_confidence"],
            data_confidence=proj_data["data_confidence"],
        )
        session.add(project)
        await session.flush()

        # Stages
        for stage_data in proj_data["stages"]:
            stage = Stage(
                project_id=project.id,
                template_stage_id=None,
                name=stage_data["name"],
                sequence_order=stage_data["sequence_order"],
                status=stage_data["status"],
                original_commitment_date=date.fromisoformat(stage_data["original_commitment_date"]) if stage_data.get("original_commitment_date") else None,
                approved_baseline_date=date.fromisoformat(stage_data["approved_baseline_date"]) if stage_data.get("approved_baseline_date") else None,
                planned_start=date.fromisoformat(stage_data["planned_start"]) if stage_data.get("planned_start") else None,
                actual_start=date.fromisoformat(stage_data["actual_start"]) if stage_data.get("actual_start") else None,
                actual_end=date.fromisoformat(stage_data["actual_end"]) if stage_data.get("actual_end") else None,
                delay_probability=proj_data["current_risk_score"] if stage_data["status"] == "in_progress" else None,
            )
            session.add(stage)

        # Parcels (sample)
        parcel_data_list = generate_parcels_for_project(proj_data)
        for pd in parcel_data_list[:30]:  # Limit per project for seed performance
            parcel = Parcel(
                project_id=project.id,
                ulpin=pd.get("ulpin"),
                survey_no=pd.get("survey_no"),
                village_name=pd.get("village_name"),
                district=pd.get("district"),
                area_hectares=pd.get("area_hectares"),
                land_use=pd.get("land_use"),
                acquisition_status=pd.get("acquisition_status"),
                possession_status=pd.get("possession_status"),
                criticality_weight=pd.get("criticality_weight"),
                usability_score=pd.get("usability_score"),
                is_blocking=pd.get("is_blocking"),
                encumbrance_free=pd.get("encumbrance_free", False),
                access_available=pd.get("access_available", False),
            )
            session.add(parcel)

        # Alerts
        alerts = generate_alerts_for_project(proj_data)
        for alert_data in alerts:
            alert = Alert(
                project_id=project.id,
                alert_type=alert_data["alert_type"],
                title=alert_data["title"],
                description=alert_data.get("description"),
                severity=alert_data.get("severity", "medium"),
                priority_index=alert_data.get("priority_index"),
                state="open",
            )
            session.add(alert)

    await session.flush()


async def run_seed():
    """Run the full database seeding process."""
    await init_db()

    async with async_session_factory() as session:
        try:
            print("🌱 Seeding roles...")
            roles = await seed_roles(session)

            print("👤 Seeding users...")
            await seed_users(session, roles)

            print("⚖️ Seeding legal templates...")
            template = await seed_legal_template(session)

            print("🎯 Seeding allowed actions...")
            await seed_allowed_actions(session)

            print("📡 Seeding data sources...")
            await seed_data_sources(session)

            print("🤖 Seeding model version...")
            await seed_model_version(session)

            print("🏗️ Seeding projects (100 synthetic projects)...")
            await seed_projects(session, template, n_projects=100)

            await session.commit()
            print("✅ Database seeded successfully!")

        except Exception as e:
            await session.rollback()
            print(f"❌ Seeding failed: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(run_seed())
