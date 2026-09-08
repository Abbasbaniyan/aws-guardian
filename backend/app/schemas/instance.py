from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class InstanceSummary(BaseModel):
    instance_id: str
    name: str
    state: str
    instance_type: str
    launch_time: Optional[datetime] = None
    uptime_hours: float
    environment: str
    is_protected: bool
    protection_reason: Optional[str] = None
    tags: Dict[str, str] = {}


class InstanceListResponse(BaseModel):
    total_count: int
    running_count: int
    stopped_count: int
    protected_count: int
    data_source: str  # "aws_live" or "mock_mode"
    instances: list[InstanceSummary]