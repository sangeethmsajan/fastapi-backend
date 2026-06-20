# api/routes/scan.py

import math
from typing import Optional
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.schemas.attack import AttackCreateRequest, AttackResponse, AttackListResponse
from app.db.database import get_db
from app.db.models import Attack
from app.tasks.scan_tasks import run_attack

router = APIRouter(prefix="/scan", tags=["Scan"])

VALID_STATUSES = ["Running", "Completed", "Failed", "Cancelled", "Queued"]


@router.post("", response_model=AttackResponse, status_code=status.HTTP_201_CREATED)
def create_scan(payload: AttackCreateRequest, db: Session = Depends(get_db)):
    new_attack = Attack(
        name=payload.name,
        attack_type=payload.type,
        target=payload.target,
        scope=payload.scope,
        objective=payload.objective,
        status="Queued",
    )
    db.add(new_attack)
    db.commit()
    db.refresh(new_attack)
    run_attack.delay(new_attack.id)
    return new_attack  # from_attributes handles the mapping


@router.get("", response_model=AttackListResponse)
def list_attacks(
    db: Session = Depends(get_db),
    status: Optional[str] = Query(default=None),
    search: Optional[str] = Query(default=None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
):
    base_query = db.query(Attack)

    # Status filter
    if status and status in VALID_STATUSES:
        base_query = base_query.filter(Attack.status == status)

    # Search filter
    if search and search.strip():
        term = f"%{search.strip()}%"
        base_query = base_query.filter(
            Attack.target.ilike(term) | Attack.name.ilike(term)
        )

    # Tab counts — always from full table, not affected by current filters
    counts_query = (
        db.query(Attack.status, func.count(Attack.id))
        .group_by(Attack.status)
        .all()
    )
    status_counts = {s: c for s, c in counts_query}
    counts = {
        "All":       sum(status_counts.values()),
        "Running":   status_counts.get("Running", 0),
        "Completed": status_counts.get("Completed", 0),
        "Failed":    status_counts.get("Failed", 0),
        "Cancelled": status_counts.get("Cancelled", 0),
        "Queued":    status_counts.get("Queued", 0),
    }

    # Pagination
    total = base_query.count()
    total_pages = math.ceil(total / limit) if total > 0 else 1
    attacks = (
        base_query
        .order_by(Attack.created_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    return AttackListResponse(
        attacks=attacks,
        total=total,
        counts=counts,
        page=page,
        limit=limit,
        total_pages=total_pages,
    )


@router.get("/{attack_id}", response_model=AttackResponse)
def get_attack(attack_id: int, db: Session = Depends(get_db)):
    from fastapi import HTTPException
    attack = db.query(Attack).filter(Attack.id == attack_id).first()
    if not attack:
        raise HTTPException(status_code=404, detail="Attack not found")
    return attack