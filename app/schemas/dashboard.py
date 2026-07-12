from pydantic import BaseModel
from typing import List

class KpiItem(BaseModel):
    id: int
    label: str
    value: str        # string not int — matches your frontend "7", "24"
    meta: str
    tone: str

class DashboardSummaryResponse(BaseModel):
    kpis: List[KpiItem]