from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.schemas import AttackCreateRequest, AttackResponse
from app.db.database import get_db
from app.db.models import Attack
from app.tasks.scan_tasks import run_attack

router = APIRouter(prefix="/scan", tags=["Scan"])


@router.post("", response_model=AttackResponse, status_code=status.HTTP_201_CREATED)
def create_scan(payload: AttackCreateRequest, db: Session = Depends(get_db)):
    new_attack = Attack(
        name=payload.name,
        attack_type=payload.type,
        target=payload.target,
        scope=payload.scope,
        objective=payload.objective,
        status="Queued"
    )

    db.add(new_attack)
    db.commit()
    db.refresh(new_attack)
    run_attack.delay(new_attack.id)

    return AttackResponse(
        id=new_attack.id,
        name=new_attack.name,
        type=new_attack.attack_type,
        target=new_attack.target,
        scope=new_attack.scope,
        objective=new_attack.objective,
        status=new_attack.status
    )
@router.get("", response_model=list[AttackResponse])
def list_attacks(db: Session = Depends(get_db)):
    attacks = db.query(Attack).order_by(Attack.id.desc()).all()

    return [
        AttackResponse(
            id=attack.id,
            name=attack.name,
            type=attack.attack_type,
            target=attack.target,
            scope=attack.scope,
            objective=attack.objective,
            status=attack.status
        )
        for attack in attacks
    ]
