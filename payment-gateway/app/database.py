"""
Настройка базы данных.
"""
import logging
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import text

from .config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()
engine = create_async_engine(settings.database_url, echo=False)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()


async def get_session() -> AsyncSession:
    """Получить сессию БД."""
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Инициализация БД (создание таблиц)."""
    async with engine.begin() as conn:

        await conn.execute(text("SELECT 1"))
        logger.info("Database connection established")
        

        from .models import Payment, SelfEmployedReceipt, Invoice, Act, IncomeTracking
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created/verified")

