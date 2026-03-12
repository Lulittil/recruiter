"""
Payment Gateway Service - основной файл приложения.
Обрабатывает платежи от юридических лиц и генерирует чеки самозанятого.
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from .database import engine, get_session, init_db
from .routers import payments, webhooks
from .config import get_settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения."""

    logger.info("Initializing database...")
    await init_db()
    logger.info("Database initialized")
    
    yield
    

    version="1.0.0",
    lifespan=lifespan
)

