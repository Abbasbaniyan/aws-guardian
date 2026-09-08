from typing import Dict, Any, List
from enum import Enum
from pydantic import BaseModel
from app.core.config import settings
from app.schemas.instance import InstanceSummary
from app.services.aws.cloudwatch import cloudwatch_service


class AlertSeverity(str, Enum):
    NORMAL = "normal"          # 🟢 Everything running as expected
    ATTENTION = "attention"    # 🟡 Threshold breached, potential forgotten server
    CRITICAL = "critical"      # 🔴 Extreme runtime or runaway idle non-prod


class WatchdogEvaluation(BaseModel):
    instance_id: str
    name: str
    state: str
    uptime_hours: float
    avg_cpu_percent: float
    is_protected: bool
    protection_reason: str | None
    severity: AlertSeverity
    rule_breached: bool
    trigger_reason: str
    suggested_action: str  # "NONE", "REVIEW", "STOP"


class RulesEngine:
    def __init__(self):
        self.idle_hours_threshold = settings.DEFAULT_IDLE_HOURS_THRESHOLD
        self.cpu_idle_threshold = settings.DEFAULT_CPU_IDLE_PERCENT

    def evaluate_instance(self, inst: InstanceSummary) -> WatchdogEvaluation:
        # If stopped, it consumes no compute runtime
        if inst.state != "running":
            return WatchdogEvaluation(
                instance_id=inst.instance_id,
                name=inst.name,
                state=inst.state,
                uptime_hours=inst.uptime_hours,
                avg_cpu_percent=0.0,
                is_protected=inst.is_protected,
                protection_reason=inst.protection_reason,
                severity=AlertSeverity.NORMAL,
                rule_breached=False,
                trigger_reason="Instance is stopped.",
                suggested_action="NONE",
            )

        # Retrieve factual CPU consumption
        avg_cpu = cloudwatch_service.get_average_cpu(
            inst.instance_id, hours=self.idle_hours_threshold
        )

        is_idle = avg_cpu <= self.cpu_idle_threshold
        is_long_running = inst.uptime_hours >= self.idle_hours_threshold

        # RULE 1: Protected / Production Instances
        # These can receive alerts, but suggested action can NEVER be auto-stop.
        if inst.is_protected:
            if is_idle and is_long_running:
                return WatchdogEvaluation(
                    instance_id=inst.instance_id,
                    name=inst.name,
                    state=inst.state,
                    uptime_hours=inst.uptime_hours,
                    avg_cpu_percent=avg_cpu,
                    is_protected=True,
                    protection_reason=inst.protection_reason,
                    severity=AlertSeverity.ATTENTION,
                    rule_breached=True,
                    trigger_reason=f"Production instance has low activity ({avg_cpu}% CPU). Auto-stop prohibited.",
                    suggested_action="REVIEW",
                )
            return WatchdogEvaluation(
                instance_id=inst.instance_id,
                name=inst.name,
                state=inst.state,
                uptime_hours=inst.uptime_hours,
                avg_cpu_percent=avg_cpu,
                is_protected=True,
                protection_reason=inst.protection_reason,
                severity=AlertSeverity.NORMAL,
                rule_breached=False,
                trigger_reason="Production workload within normal operating limits.",
                suggested_action="NONE",
            )

        # RULE 2: Non-protected instance exceeding idle duration
        if is_idle and is_long_running:
            # If runtime is 3x threshold, mark CRITICAL
            severity = (
                AlertSeverity.CRITICAL
                if inst.uptime_hours >= (self.idle_hours_threshold * 3)
                else AlertSeverity.ATTENTION
            )
            return WatchdogEvaluation(
                instance_id=inst.instance_id,
                name=inst.name,
                state=inst.state,
                uptime_hours=inst.uptime_hours,
                avg_cpu_percent=avg_cpu,
                is_protected=False,
                protection_reason=None,
                severity=severity,
                rule_breached=True,
                trigger_reason=f"Idle detected: Running for {inst.uptime_hours}h with avg CPU of {avg_cpu}%.",
                suggested_action="STOP",
            )

        # RULE 3: Active non-protected instance
        return WatchdogEvaluation(
            instance_id=inst.instance_id,
            name=inst.name,
            state=inst.state,
            uptime_hours=inst.uptime_hours,
            avg_cpu_percent=avg_cpu,
            is_protected=False,
            protection_reason=None,
            severity=AlertSeverity.NORMAL,
            rule_breached=False,
            trigger_reason="Instance is actively processing workloads.",
            suggested_action="NONE",
        )

    def evaluate_all(self, instances: List[InstanceSummary]) -> List[WatchdogEvaluation]:
        return [self.evaluate_instance(inst) for inst in instances]


rules_engine = RulesEngine()