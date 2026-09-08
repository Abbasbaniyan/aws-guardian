from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.models.audit import init_db
from app.api.health import router as health_router
from app.api.instances import router as instances_router
from app.api.watchdog import router as watchdog_router
from app.api.ai import router as ai_router
from app.api.actions import router as actions_router

# Initialize SQLite database schema
init_db()

app = FastAPI(
    title=settings.APP_NAME,
    description="Intelligent, lightweight AWS EC2 Watchdog",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Attach API routers
app.include_router(health_router, prefix="/api", tags=["System"])
app.include_router(instances_router, prefix="/api", tags=["EC2 Discovery"])
app.include_router(watchdog_router, prefix="/api", tags=["Watchdog Rules Engine"])
app.include_router(ai_router, prefix="/api", tags=["AI Intelligence Layer"])
app.include_router(actions_router, prefix="/api", tags=["Safe Action Executor"])


@app.get("/")
def root():
    return {
        "message": "AWS Guardian API is active.",
        "health": "/api/health",
        "instances": "/api/instances",
        "evaluate": "/api/watchdog/evaluate",
        "brief": "/api/brief",
        "audit": "/api/audit",
    }