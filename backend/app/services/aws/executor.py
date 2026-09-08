from datetime import datetime, timezone
from typing import Tuple, Dict, Any
from botocore.exceptions import ClientError, NoCredentialsError
from app.services.aws.ec2 import ec2_service
from app.models.audit import ActionAuditLog, SessionLocal


class ActionExecutor:
    """
    Deterministic Action Gate:
    Enforces safety policies before performing any mutation on AWS infrastructure.
    """

    def stop_instance(self, instance_id: str, actor: str = "user") -> Tuple[bool, str]:
        db = SessionLocal()
        try:
            instances, source = ec2_service.fetch_instances()
            target = next((i for i in instances if i.instance_id == instance_id), None)

            if not target:
                msg = f"Instance {instance_id} was not found in discovered inventory."
                self._record_audit(db, instance_id, "unknown", "STOP", actor, "FAILED", msg, False)
                return False, msg

            # HARD SAFETY GATE 1: Production Protection
            if target.is_protected:
                msg = f"BLOCKED: Instance {target.name} ({instance_id}) is PROTECTED. {target.protection_reason}"
                self._record_audit(db, instance_id, target.name, "STOP", actor, "BLOCKED", msg, True)
                return False, msg

            # HARD SAFETY GATE 2: State check
            if target.state != "running":
                msg = f"ABORTED: Instance {target.name} ({instance_id}) is currently in '{target.state}' state."
                self._record_audit(db, instance_id, target.name, "STOP", actor, "FAILED", msg, False)
                return False, msg

            # EXECUTION: Real AWS vs. Safe Mock Mode
            if source == "aws_live":
                client = ec2_service._get_client()
                client.stop_instances(InstanceIds=[instance_id])
                msg = f"SUCCESS: AWS ec2:StopInstances executed for {target.name} ({instance_id})."
            else:
                msg = f"SUCCESS [MOCK MODE]: Simulating safe stop for non-prod instance {target.name} ({instance_id})."

            self._record_audit(db, instance_id, target.name, "STOP", actor, "SUCCESS", msg, False)
            return True, msg

        except (ClientError, Exception) as e:
            err_msg = f"AWS API Error: {str(e)}"
            self._record_audit(db, instance_id, "unknown", "STOP", actor, "FAILED", err_msg, False)
            return False, err_msg
        finally:
            db.close()

    def _record_audit(self, db, inst_id, name, action, actor, status, reason, is_protected):
        log = ActionAuditLog(
            instance_id=inst_id,
            instance_name=name,
            action_type=action,
            initiated_by=actor,
            status=status,
            reason=reason,
            is_protected_target=is_protected,
        )
        db.add(log)
        db.commit()


action_executor = ActionExecutor()