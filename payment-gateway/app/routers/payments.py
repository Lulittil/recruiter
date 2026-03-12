"""
Роутеры для обработки платежей.
"""
import logging
from typing import Optional
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy import select
from decimal import Decimal

from ..database import get_session
from ..models import Payment, SelfEmployedReceipt, IncomeTracking
from ..schemas import PaymentCreate, PaymentDTO, PaymentResponse, SelfEmployedReceiptCreate
from ..payment_providers.robokassa import RobokassaProvider
from ..payment_providers.selfwork import SelfworkProvider
from ..services.receipt_service import ReceiptService
from ..services.income_service import IncomeService
from ..config import get_settings

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/payments", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def create_payment(
    payment_data: PaymentCreate,
    session: AsyncSession = Depends(get_session)
) -> PaymentResponse:
    """Создать новый платеж."""
    try:
        settings = get_settings()
        is_test_mode = settings.is_test
        

        metadata = {}
        if payment_data.company_info:
            metadata["company_info"] = payment_data.company_info
        if payment_data.telegram_data:
            metadata["telegram_data"] = payment_data.telegram_data
        

        db_payment = Payment(
            user_id=payment_data.user_id,
            vacancy_id=payment_data.vacancy_id,
            payment_type=payment_data.payment_type,
            amount=payment_data.amount,
            currency=payment_data.currency,
            status="pending",
            payment_metadata=metadata if metadata else None
        )
        session.add(db_payment)
        await session.flush()  