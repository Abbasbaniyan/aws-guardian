from fastapi import APIRouter
from app.services.aws.ec2 import ec2_service
from app.schemas.instance import InstanceListResponse

router = APIRouter()


@router.get("/instances", response_model=InstanceListResponse)
def get_monitored_instances():
    instances, source = ec2_service.fetch_instances()

    running = sum(1 for i in instances if i.state == "running")
    stopped = sum(1 for i in instances if i.state == "stopped")
    protected = sum(1 for i in instances if i.is_protected)

    return InstanceListResponse(
        total_count=len(instances),
        running_count=running,
        stopped_count=stopped,
        protected_count=protected,
        data_source=source,
        instances=instances,
    )