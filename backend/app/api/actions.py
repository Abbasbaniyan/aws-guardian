from fastapi import APIRouter, HTTPException
from typing import List
from app.schemas.action import StopInstanceRequest, ActionResponse, AuditLogItem
from app.services.aws.executor import action_executor
from app.models.audit import ActionAuditLog, SessionLocal

router = APIRouter()


@router.post("/instances/stop", response_model=ActionResponse)
def stop_instance(request: StopInstanceRequest):
    if not request.confirmed:
        raise HTTPException(
            status_code=400,
            detail="Safety confirmation required. Set 'confirmed: true' to authorize.",
        )

    success, message = action_executor.stop_instance(request.instance_id)

    if not success and "BLOCKED" in message:
        raise HTTPException(status_code=403, detail=message)
    elif not success:
        raise HTTPException(status_code=400, detail=message)

    return ActionResponse(
        success=success,
        message=message,
        instance_id=request.instance_id,
    )


@router.get("/audit", response_model=List[AuditLogItem])
def get_audit_trail():
    db = SessionLocal()
    try:
        logs = db.query(ActionAuditLog).order_by(ActionAuditLog.id.desc()).limit(50).all()
        return logs
    finally:
        db.close()