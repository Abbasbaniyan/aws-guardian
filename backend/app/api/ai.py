from fastapi import APIRouter
from app.services.aws.ec2 import ec2_service
from app.services.rules.engine import rules_engine
from app.services.ai.analyzer import ai_analyzer
from app.schemas.ai import DailyBriefResponse

router = APIRouter()


@router.get("/brief", response_model=DailyBriefResponse)
def get_ai_daily_brief():
    instances, _ = ec2_service.fetch_instances()
    evaluations = rules_engine.evaluate_all(instances)
    return ai_analyzer.generate_daily_brief(evaluations)