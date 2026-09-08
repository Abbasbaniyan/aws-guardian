from fastapi import APIRouter
from typing import List
from app.services.aws.ec2 import ec2_service
from app.services.rules.engine import rules_engine, WatchdogEvaluation

router = APIRouter()


@router.get("/watchdog/evaluate", response_model=List[WatchdogEvaluation])
def evaluate_infrastructure():
    instances, _ = ec2_service.fetch_instances()
    return rules_engine.evaluate_all(instances)