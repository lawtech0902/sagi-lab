from fastapi import APIRouter

from app.api.v1.endpoints import health, alerts, triage, analysis


api_router = APIRouter()

api_router.include_router(health.router, tags=["health"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["alerts"])
api_router.include_router(triage.router, prefix="/triage", tags=["triage"])
api_router.include_router(analysis.router, prefix="/analysis", tags=["analysis"])
