import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from datetime import datetime, timezone
from typing import List, Dict, Any, Tuple
from app.core.config import settings
from app.schemas.instance import InstanceSummary


class EC2Service:
    def __init__(self):
        self.region = settings.AWS_REGION
        self.protected_key = settings.PROTECTED_TAG_KEY
        self.protected_val = settings.PROTECTED_TAG_VALUE.lower()

    def _get_client(self):
        """Initializes Boto3 EC2 client using explicit keys or local AWS profile/IAM role."""
        if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
            return boto3.client(
                "ec2",
                region_name=self.region,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            )
        return boto3.client("ec2", region_name=self.region)

    def _evaluate_protection(
        self, tags: Dict[str, str], name: str
    ) -> Tuple[bool, str]:
        """
        DETERMINISTIC RULE:
        Instance is protected if:
        1. Environment tag matches 'production'
        2. Protected tag == 'true'
        3. Name starts with 'prod-'
        """
        env = tags.get(self.protected_key, "").strip().lower()
        if env == self.protected_val:
            return True, f"Tag [{self.protected_key}={tags.get(self.protected_key)}] is locked as production."

        if tags.get("Protected", "").strip().lower() == "true":
            return True, "Tag [Protected=true] explicitly prevents automatic actions."

        if name.lower().startswith("prod-"):
            return True, "Instance name begins with production prefix 'prod-'."

        return False, "Instance is not flagged as production or protected."

    def _parse_instance(self, raw: Dict[str, Any]) -> InstanceSummary:
        instance_id = raw.get("InstanceId", "unknown")
        state = raw.get("State", {}).get("Name", "unknown")
        instance_type = raw.get("InstanceType", "t2.micro")
        launch_time = raw.get("LaunchTime")

        # Parse tags
        tags = {t.get("Key", ""): t.get("Value", "") for t in raw.get("Tags", []) if t.get("Key")}
        name = tags.get("Name", instance_id)
        environment = tags.get("Environment", "development")

        # Calculate uptime in hours
        uptime_hours = 0.0
        if launch_time and state == "running":
            now = datetime.now(timezone.utc)
            uptime_hours = round((now - launch_time).total_seconds() / 3600.0, 2)

        is_protected, reason = self._evaluate_protection(tags, name)

        return InstanceSummary(
            instance_id=instance_id,
            name=name,
            state=state,
            instance_type=instance_type,
            launch_time=launch_time,
            uptime_hours=uptime_hours,
            environment=environment,
            is_protected=is_protected,
            protection_reason=reason,
            tags=tags,
        )

    def _mock_instances(self) -> List[InstanceSummary]:
        """Realistic mock fallback for local testing without active AWS billing."""
        now = datetime.now(timezone.utc)
        return [
            InstanceSummary(
                instance_id="i-0a123456789abcdef",
                name="dev-server-01",
                state="running",
                instance_type="t3.medium",
                launch_time=now,
                uptime_hours=14.5,
                environment="development",
                is_protected=False,
                protection_reason="Instance is not flagged as production or protected.",
                tags={"Name": "dev-server-01", "Environment": "development", "Team": "Frontend"},
            ),
            InstanceSummary(
                instance_id="i-0b987654321fedcba",
                name="prod-api-gateway",
                state="running",
                instance_type="t3.large",
                launch_time=now,
                uptime_hours=240.2,
                environment="production",
                is_protected=True,
                protection_reason="Tag [Environment=production] is locked as production.",
                tags={"Name": "prod-api-gateway", "Environment": "production", "Tier": "Core"},
            ),
            InstanceSummary(
                instance_id="i-0c112233445566778",
                name="qa-testing-node",
                state="stopped",
                instance_type="t2.micro",
                launch_time=None,
                uptime_hours=0.0,
                environment="testing",
                is_protected=False,
                protection_reason="Instance is not flagged as production or protected.",
                tags={"Name": "qa-testing-node", "Environment": "testing"},
            ),
        ]

    def fetch_instances(self) -> Tuple[List[InstanceSummary], str]:
        """Fetches instances from AWS EC2, falls back to deterministic mock if no credentials."""
        try:
            client = self._get_client()
            response = client.describe_instances()
            instances: List[InstanceSummary] = []

            for reservation in response.get("Reservations", []):
                for inst in reservation.get("Instances", []):
                    instances.append(self._parse_instance(inst))

            return instances, "aws_live"

        except (NoCredentialsError, ClientError):
            # Safe offline fallback for local verification
            return self._mock_instances(), "mock_mode"


ec2_service = EC2Service()