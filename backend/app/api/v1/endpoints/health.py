from fastapi import APIRouter
from sqlalchemy import text
from app.db.session import AsyncSessionLocal

router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    db_status = "disconnected"
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
            db_status = "connected"
    except Exception:
        pass

    return {"status": "healthy", "database": db_status, "version": "0.1.0"}
