from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class AttackCreateRequest(BaseModel):
    name: str
    type: str
    target: str
    scope: Optional[str] = None
    objective: Optional[str] = None


class AttackResponse(BaseModel):
    id: int
    name: str
    type: str = Field(alias="attack_type")  # ← reads attack_type from DB, sends as type
    target: str
    scope: Optional[str] = None
    objective: Optional[str] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
        populate_by_name = True   # ← allows both field name and alias to work


class AttackListResponse(BaseModel):
    attacks: list[AttackResponse]
    total: int
    counts: dict[str, int]
    page: int
    limit: int
    total_pages: int