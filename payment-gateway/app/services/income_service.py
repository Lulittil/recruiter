"""
Сервис для отслеживания дохода самозанятого.
"""
import logging
from datetime import datetime
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..models import IncomeTracking

logger = logging.getLogger(__name__)

INCOME_LIMIT = 2_400_000  