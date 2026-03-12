"""
Роутеры для работы с чеками самозанятого.
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..database import get_session
from ..models import SelfEmployedReceipt
from ..schemas import SelfEmployedReceiptDTO
from ..services.receipt_service import ReceiptService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/receipts/{receipt_id}", response_model=SelfEmployedReceiptDTO)
async def get_receipt(
    receipt_id: int,
    session: AsyncSession = Depends(get_session)
) -> SelfEmployedReceiptDTO:
    """Получить информацию о чеке."""
    result = await session.execute(
        select(SelfEmployedReceipt).where(SelfEmployedReceipt.receipt_id == receipt_id)
    )
    receipt = result.scalar_one_or_none()
    
    if not receipt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Чек не найден"
        )
    
    return SelfEmployedReceiptDTO.model_validate(receipt)


@router.post("/receipts/{receipt_id}/sync")
async def sync_receipt(
    receipt_id: int,
    session: AsyncSession = Depends(get_session)
):
    """Синхронизировать чек с "Мой налог"."""
    from ..models import Payment
    
    result = await session.execute(
        select(SelfEmployedReceipt).where(SelfEmployedReceipt.receipt_id == receipt_id)
    )
    receipt = result.scalar_one_or_none()
    
    if not receipt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Чек не найден"
        )
    

    from datetime import datetime
    from ..services.income_service import IncomeService
    
    if year is None:
        year = datetime.now().year
    

    income_service = IncomeService()
    tracking = await income_service.get_income_status(session, year)
    

    
    response = {
        "year": year,
        "total_income": float(tracking.total_income),
        "income_from_individuals": float(tracking.income_from_individuals),
        "income_from_legal_entities": float(tracking.income_from_legal_entities),
        "tax_paid": float(tracking.tax_paid),
        "limit": 2_400_000,
        "remaining": 2_400_000 - float(tracking.total_income),
        "limit_exceeded": tracking.limit_exceeded,
        "source": "database"
    }
    

    if api_data:
        response.update({
            "total_income": api_data["total_income"],
            "remaining": api_data["remaining"],
            "limit_exceeded": api_data["limit_exceeded"],
            "source": "api"
        })
    
    return response

