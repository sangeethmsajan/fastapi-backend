from pydantic import BaseModel


class DashboardSummaryResponse(BaseModel):
    active_attacks: int
    completed: int
    critical_findings: int
    agents_online: int