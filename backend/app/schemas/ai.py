from pydantic import BaseModel
from typing import Optional, List
from app.services.rules.engine import AlertSeverity


class AIHeadsUp(BaseModel):
    instance_id: str
    instance_name: str
    severity: AlertSeverity
    runtime_formatted: str
    normal_runtime_formatted: str
    inactivity_formatted: str
    headline: str
    explanation: str
    estimated_waste_cost_usd: float
    recommended_action: str
    can_execute_auto_stop: bool


class DailyBriefResponse(BaseModel):
    total_monitored: int
    normal_count: int
    attention_count: int
    critical_count: int
    potential_unnecessary_runtime_hours: float
    headline_summary: str
    alerts: List[AIHeadsUp]