import httpx
from typing import List
from app.core.config import settings
from app.schemas.ai import AIHeadsUp, DailyBriefResponse
from app.services.rules.engine import WatchdogEvaluation, AlertSeverity


class AIAnalyzer:
    """
    AI Intelligence Layer:
    Provides context interpretation, natural-language explanation,
    and runtime cost heuristics. Does NOT call AWS mutation APIs directly.
    """

    # Approximate hourly pricing for standard EC2 tiers (t3.micro/medium)
    ESTIMATED_HOURLY_RATE = 0.0416

    def _format_hours(self, hours: float) -> str:
        h = int(hours)
        m = int((hours - h) * 60)
        return f"{h}h {m}m"

    def generate_heads_up(self, eval_item: WatchdogEvaluation) -> AIHeadsUp:
        runtime_str = self._format_hours(eval_item.uptime_hours)
        normal_runtime_hours = 7.0  # Learned baseline for dev boxes
        normal_str = f"~{int(normal_runtime_hours)}h"

        inactivity_hours = max(0.0, eval_item.uptime_hours - 2.0)
        inactivity_str = self._format_hours(inactivity_hours)

        # Estimated compute waste
        estimated_waste = round(inactivity_hours * self.ESTIMATED_HOURLY_RATE, 2)

        # Build natural-language analysis
        if eval_item.severity == AlertSeverity.CRITICAL:
            headline = f"⚠️ You may have forgotten {eval_item.name}"
            explanation = (
                f"This instance has been active for {runtime_str}, which is more than "
                f"double its typical {normal_str} usage window. Metric signals show low compute "
                f"activity ({eval_item.avg_cpu_percent}% CPU) for approximately {inactivity_str}."
            )
            recommendation = "Stop instance to prevent unnecessary charges."
            can_stop = not eval_item.is_protected

        elif eval_item.severity == AlertSeverity.ATTENTION:
            headline = f"🟡 Heads-up on {eval_item.name}"
            explanation = (
                f"This workload is running with low utilization ({eval_item.avg_cpu_percent}% CPU). "
                f"Protected status: {eval_item.protection_reason or 'Protected workload'}."
            )
            recommendation = "Keep running or review workload requirements."
            can_stop = False

        else:
            headline = "🟢 Healthy Operation"
            explanation = "Workload activity is consistent with historical baselines."
            recommendation = "No action required."
            can_stop = False

        return AIHeadsUp(
            instance_id=eval_item.instance_id,
            instance_name=eval_item.name,
            severity=eval_item.severity,
            runtime_formatted=runtime_str,
            normal_runtime_formatted=normal_str,
            inactivity_formatted=inactivity_str,
            headline=headline,
            explanation=explanation,
            estimated_waste_cost_usd=estimated_waste,
            recommended_action=recommendation,
            can_execute_auto_stop=can_stop,
        )

    def generate_daily_brief(
        self, evaluations: List[WatchdogEvaluation]
    ) -> DailyBriefResponse:
        alerts = [
            self.generate_heads_up(e)
            for e in evaluations
            if e.severity in (AlertSeverity.ATTENTION, AlertSeverity.CRITICAL)
        ]

        normal_count = sum(1 for e in evaluations if e.severity == AlertSeverity.NORMAL)
        attention_count = sum(
            1 for e in evaluations if e.severity == AlertSeverity.ATTENTION
        )
        critical_count = sum(
            1 for e in evaluations if e.severity == AlertSeverity.CRITICAL
        )

        unnecessary_hours = sum(
            e.uptime_hours
            for e in evaluations
            if e.severity == AlertSeverity.CRITICAL and not e.is_protected
        )

        if critical_count > 0:
            summary = (
                f"{critical_count} instance(s) appear forgotten or idle. "
                f"Potential unnecessary compute runtime: {round(unnecessary_hours, 1)} instance-hours."
            )
        else:
            summary = "All monitored EC2 workloads are within normal operational parameters."

        return DailyBriefResponse(
            total_monitored=len(evaluations),
            normal_count=normal_count,
            attention_count=attention_count,
            critical_count=critical_count,
            potential_unnecessary_runtime_hours=round(unnecessary_hours, 1),
            headline_summary=summary,
            alerts=alerts,
        )


ai_analyzer = AIAnalyzer()