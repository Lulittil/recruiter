"""
Pydantic схемы для валидации данных.
"""
from datetime import datetime
from typing import Optional
from decimal import Decimal
from pydantic import BaseModel, Field


class PaymentCreate(BaseModel):
    """Схема создания платежа."""
    user_id: int
    vacancy_id: Optional[int] = None
    payment_type: str = Field(..., pattern="^(individual|legal_entity)$")
    amount: Decimal
    currency: str = "RUB"
    company_info: Optional[dict] = None  