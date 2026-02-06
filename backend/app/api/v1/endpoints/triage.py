from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.alert_service import AlertService
from app.services.triage_service import TriageService
from app.schemas.triage import (
    TriageAnalysisRequest,
    TriageAnalysisResponse,
)
from app.triage.graph import create_triage_graph
from app.pkg.logger import logger

router = APIRouter()


@router.post("/analyze", response_model=TriageAnalysisResponse)
async def analyze_alert(
    request: TriageAnalysisRequest,
    db: AsyncSession = Depends(get_db),
):
    """Submit alert JSON for triage analysis"""
    alert_service = AlertService(db)
    graph = create_triage_graph()
    triage_service = TriageService(db, graph)

    try:
        # Create alert from raw data
        alert = await alert_service.create_alert(request.alert_data)

        # Run triage pipeline
        result = await triage_service.analyze_alert(alert)

        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Triage analysis failed: {str(e)}")


@router.post("/{alert_id}", response_model=TriageAnalysisResponse)
async def trigger_triage(alert_id: UUID, db: AsyncSession = Depends(get_db)):
    logger.info(f"Triggering manual triage for alert: {alert_id}")
    service = TriageService(db)
    return await service.run_triage(alert_id)


@router.post("/reanalyze/{alert_id}", response_model=TriageAnalysisResponse)
async def reanalyze_alert(
    alert_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Re-run triage analysis on existing alert"""
    alert_service = AlertService(db)
    graph = create_triage_graph()
    triage_service = TriageService(db, graph)

    # Get existing alert
    alert = await alert_service.get_alert_by_id(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    try:
        # Delete existing triage result if any
        await triage_service.delete_triage_result(alert_id)

        # Re-run triage pipeline
        result = await triage_service.analyze_alert(alert)

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Triage analysis failed: {str(e)}")
