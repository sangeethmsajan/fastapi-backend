from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Attack
from app.schemas.dashboard import DashboardSummaryResponse

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=DashboardSummaryResponse)
def get_dashboard_summary(db: Session = Depends(get_db)):
    active_attacks = (
        db.query(func.count(Attack.id))
        .filter(Attack.status.in_(["Queued", "Running"]))
        .scalar()
    )

    completed = (
        db.query(func.count(Attack.id))
        .filter(Attack.status == "Completed")
        .scalar()
    )

    return DashboardSummaryResponse(
        active_attacks=active_attacks or 0,
        completed=completed or 0,
        critical_findings=0,
        agents_online=1,
    )