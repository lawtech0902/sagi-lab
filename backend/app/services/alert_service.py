from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from sqlalchemy import select, func, or_, any_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.alert import Alert
from app.pkg.logger import logger
from app.models.triage_result import TriageResult
from app.utils.constants import SEVERITY_MAP
from app.utils.common import parse_ip_list, parse_single_ip, parse_time
from app.pkg.logger import logger
from datetime import timedelta


class AlertService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_alerts(
        self,
        page: int = 1,
        page_size: int = 20,
        sort_by: str = "upload_time",
        sort_order: str = "desc",
        filters: Optional[Dict[str, Any]] = None,
    ) -> tuple[List[Alert], int]:
        """Get paginated and filtered alerts"""
        # Build query with triage result
        query = select(Alert).options(selectinload(Alert.triage_result))

        # Apply filters
        if filters:
            if filters.get("alert_level"):
                query = query.where(Alert.alert_level == filters["alert_level"])
            if filters.get("source_ip"):
                query = query.where(Alert.source_ip == filters["source_ip"])
            if filters.get("destination_ip"):
                query = query.where(Alert.destination_ip == filters["destination_ip"])
            if filters.get("host_ip"):
                query = query.where(Alert.host_ip == filters["host_ip"])
            if filters.get("verdict"):
                query = query.join(Alert.triage_result).where(
                    TriageResult.verdict == filters["verdict"]
                )
            if filters.get("tactic"):
                query = query.join(Alert.triage_result).where(
                    filters["tactic"] == any_(TriageResult.tactics)
                )

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total = await self.db.scalar(count_query) or 0

        # Apply sorting
        valid_sort_fields = [
            "upload_time",
            "first_alert_time",
            "last_alert_time",
            "alert_level",
            "alert_name",
        ]
        if sort_by not in valid_sort_fields:
            sort_by = "upload_time"

        order_col = getattr(Alert, sort_by)
        if sort_order == "desc":
            order_col = order_col.desc()
        query = query.order_by(order_col)

        # Apply pagination
        query = query.limit(page_size).offset((page - 1) * page_size)

        # Execute
        result = await self.db.execute(query)
        alerts = list(result.scalars().all())

        return alerts, total

    async def get_alert_by_id(self, alert_id: UUID) -> Optional[Alert]:
        """Get alert by ID with full triage details"""
        query = (
            select(Alert)
            .options(
                selectinload(Alert.triage_result).selectinload(TriageResult.entities)
            )
            .where(Alert.id == alert_id)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create_alert(self, alert_data: dict) -> Alert:
        """Create new alert from raw data"""
        base_info = alert_data.get("base_alert_info") or {}

        alert_name = base_info.get("name") or "Unknown Alert"

        # Severity mapping
        severity_val = base_info.get("severity")
        alert_level = SEVERITY_MAP.get(severity_val, "Medium")

        # IP extraction
        source_ip = parse_ip_list(base_info.get("src_ip"))
        destination_ip = parse_ip_list(base_info.get("dst_ip"))
        host_ip = parse_single_ip(base_info.get("host_ip"))

        # Timestamp parsing
        first_time = parse_time(base_info.get("first_time"))
        last_time = parse_time(base_info.get("last_time"))

        alert = Alert(
            alert_name=alert_name,
            alert_level=alert_level,
            source_ip=source_ip,
            destination_ip=destination_ip,
            host_ip=host_ip,
            first_alert_time=first_time,
            last_alert_time=last_time,
            raw_data=alert_data,
        )

        self.db.add(alert)
        await self.db.commit()
        await self.db.refresh(alert)

        logger.info(f"Alert created successfully: {alert.id}")
        return alert

    async def get_alert_stats(self) -> dict:
        """Get alert statistics for dashboard"""
        # Calculate stats for the last 24 hours (or all time if preferred, UI says 24h)
        # For now, let's do all time or maybe last 7 days to ensure data show up in demo
        last_24h = datetime.utcnow() - timedelta(hours=24)

        # Count by level
        query = select(Alert.alert_level, func.count(Alert.id)).group_by(
            Alert.alert_level
        )
        result = await self.db.execute(query)
        level_counts = dict(result.all())

        # Colors for UI
        colors = {
            "Critical": "#ef4444",
            "High": "#f97316",
            "Medium": "#eab308",
            "Low": "#3b82f6",
            "Info": "#64748b",
        }

        stats_data = []
        total_critical = 0

        # Ensure all levels are present even if count is 0
        for level in ["Critical", "High", "Medium", "Low"]:
            count = level_counts.get(level, 0)
            if level == "Critical":
                total_critical = count

            stats_data.append(
                {"name": level, "count": count, "color": colors.get(level, "#64748b")}
            )

        return {"total_critical": total_critical, "by_level": stats_data}
