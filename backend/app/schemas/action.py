from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class StopInstanceRequest(BaseModel):
    instance_id: str
    confirmed: bool = False


class ActionResponse(BaseModel):
    success: bool
    message: str
    instance_id: str


class AuditLogItem(BaseModel):
    id: int
    timestamp: datetime
    instance_id: str
    instance_name: str
    action_type: str
    initiated_by: str
    status: str
    reason: str
    is_protected_target: bool

    class Config:
        from_attributes = True