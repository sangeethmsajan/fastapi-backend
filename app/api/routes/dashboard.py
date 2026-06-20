# api/routes/dashboard.py

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.db.database import get_db
from app.db.models import Attack
from app.schemas.dashboard import DashboardSummaryResponse, KpiItem

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=DashboardSummaryResponse)
def get_dashboard_summary(db: Session = Depends(get_db)):

    # ── Today and yesterday boundaries ───────────────────────────────
    now = datetime.utcnow()
    start_of_today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    start_of_yesterday = start_of_today - timedelta(days=1)

    # ── Active attacks ────────────────────────────────────────────────
    active_now = (
        db.query(func.count(Attack.id))
        .filter(Attack.status.in_(["Queued", "Running"]))
        .scalar() or 0
    )

    active_yesterday = (
        db.query(func.count(Attack.id))
        .filter(Attack.status.in_(["Queued", "Running"]))
        .filter(Attack.created_at < start_of_today)
        .filter(Attack.created_at >= start_of_yesterday)
        .scalar() or 0
    )

    active_diff = active_now - active_yesterday

    # ── Completed attacks ─────────────────────────────────────────────
    completed_now = (
        db.query(func.count(Attack.id))
        .filter(Attack.status == "Completed")
        .scalar() or 0
    )

    completed_yesterday = (
        db.query(func.count(Attack.id))
        .filter(Attack.status == "Completed")
        .filter(Attack.created_at < start_of_today)
        .filter(Attack.created_at >= start_of_yesterday)
        .scalar() or 0
    )

    completed_diff = completed_now - completed_yesterday

    # ── Critical findings (hardcoded until Vulnerability table exists) ─
    critical_now = 0
    critical_diff = 0

    # ── Agents online (hardcoded until Agent model exists) ────────────
    agents_online = 1

    # ── Helper: format diff as meta string ───────────────────────────
    def format_diff(diff: int) -> str:
        if diff > 0:
            return f"+{diff} from yesterday"
        if diff < 0:
            return f"{diff} from yesterday"
        return "Same as yesterday"

    # ── Build KPI list matching your frontend shape ───────────────────
    kpis = [
        KpiItem(
            id=1,
            label="Active Attacks",
            value=str(active_now),
            meta=format_diff(active_diff),
            tone="blue",
        ),
        KpiItem(
            id=2,
            label="Completed",
            value=str(completed_now),
            meta=format_diff(completed_diff),
            tone="purple",
        ),
        KpiItem(
            id=3,
            label="Critical Findings",
            value=str(critical_now),
            meta=format_diff(critical_diff),
            tone="red",
        ),
        KpiItem(
            id=4,
            label="Agents Online",
            value=str(agents_online),
            meta="All systems operational",
            tone="green",
        ),
    ]

    return DashboardSummaryResponse(kpis=kpis)

@router.get("/active-attacks")
def get_active_attacks(db: Session = Depends(get_db)):
    attacks = (
        db.query(Attack)
        .filter(Attack.status.in_(["Running", "Queued"]))
        .order_by(Attack.created_at.desc())
        .limit(5)
        .all()
    )

    running_count = (
        db.query(func.count(Attack.id))
        .filter(Attack.status == "Running")
        .scalar() or 0
    )

    return {
        "running_count": running_count,
        "attacks": [
            {
                "id": a.id,
                "target": a.target,
                "scope": a.scope,
                "type": a.attack_type,
                "status": a.status,
            }
            for a in attacks
        ]
    }