from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.alert_service import AlertService
from app.schemas.alert import AlertListResponse, AlertDetail, AlertCreate, AlertResponse
from app.pkg.logger import logger

router = APIRouter()


@router.post("/", response_model=AlertResponse, status_code=201)
async def create_alert(alert_in: AlertCreate, db: AsyncSession = Depends(get_db)):
    logger.info(
        f"Received alert creation request: {alert_in.base_alert_info.get('name', 'Unknown')}"
    )
    service = AlertService(db)
    return await service.create_alert(alert_in.model_dump())


@router.get("", response_model=AlertListResponse)
async def list_alerts(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    sort_by: str = Query("upload_time", description="Sort field"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$", description="Sort order"),
    alert_level: Optional[str] = Query(None, description="Filter by alert level"),
    verdict: Optional[str] = Query(None, description="Filter by verdict"),
    source_ip: Optional[str] = Query(None, description="Filter by source IP"),
    destination_ip: Optional[str] = Query(None, description="Filter by destination IP"),
    host_ip: Optional[str] = Query(None, description="Filter by host IP"),
    tactic: Optional[str] = Query(None, description="Filter by tactic"),
    db: AsyncSession = Depends(get_db),
):
    """List all alerts with pagination and filtering"""
    service = AlertService(db)

    filters = {
        "alert_level": alert_level,
        "verdict": verdict,
        "source_ip": source_ip,
        "destination_ip": destination_ip,
        "host_ip": host_ip,
        "tactic": tactic,
    }
    # Remove None values
    filters = {k: v for k, v in filters.items() if v is not None}

    alerts, total = await service.get_alerts(
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
        filters=filters,
    )

    total_pages = (total + page_size - 1) // page_size if total > 0 else 1

    return AlertListResponse(
        items=alerts,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/{alert_id}", response_model=AlertDetail)
async def get_alert(
    alert_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get alert detail by ID"""
    service = AlertService(db)
    alert = await service.get_alert_by_id(alert_id)

    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    return alert


@router.get("/stats/dashboard", response_model=dict)
async def get_alert_stats(
    db: AsyncSession = Depends(get_db),
):
    """Get dashboard statistics"""
    service = AlertService(db)
    return await service.get_alert_stats()
