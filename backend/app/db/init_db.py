import asyncio
import logging

from app.db.session import engine
from app.models.base import Base
from app.models import *  # noqa: F401, F403


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def init_db():
    async with engine.begin() as conn:
        # Create all tables
        logger.info("Creating all tables...")
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Tables created successfully.")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(init_db())
