from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.triage.graph import TriageGraph, create_triage_graph
from app.schemas.triage import TriageAnalysisResponse
from app.db.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.alert_service import AlertService
from app.services.triage_service import TriageService

router = APIRouter()


class AnalysisRequest(BaseModel):
    alert_payload: Dict[str, Any]


@router.post("/alert", response_model=Dict[str, Any])
async def analyze_alert_payload(
    request: AnalysisRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Analyze alert payload and SAVE to DB.
    """
    alert_service = AlertService(db)
    graph = create_triage_graph()
    triage_service = TriageService(db, graph)

    try:
        # 1. Create Alert in DB
        # The service expects "alert_data" but we have "alert_payload". They serve the same purpose.
        alert = await alert_service.create_alert(request.alert_payload)

        # 2. Run Triage & Save Results
        result = await triage_service.analyze_alert(alert)

        # 3. Convert Pydantic Result model to Dict for consistency with frontend
        return result.model_dump()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
