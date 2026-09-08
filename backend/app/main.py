from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.health import router as health_router
from app.api.instances import router as instances_router

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
app.include_router(instances_router, prefix="/api", tags=["EC2 Watchdog"])


@app.get("/")
def root():
    return {
        "message": "AWS Guardian API is active.",
        "docs": "/docs",
        "health": "/api/health",
        "instances": "/api/instances",
    }