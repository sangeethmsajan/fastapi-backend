from typing import Literal
from pydantic import BaseModel, Field


class AttackCreateRequest(BaseModel):
    name: str = Field(..., min_length=3, max_length=150)
    type: Literal["internal", "external"]
    target: str = Field(..., min_length=1, max_length=255)
    scope: str | None = Field(default=None, max_length=1000)
    objective: str | None = Field(default=None, max_length=1000)


class AttackResponse(BaseModel):
    id: int
    name: str
    type: Literal["internal", "external"]
    target: str
    scope: str | None = None
    objective: str | None = None
    status: str