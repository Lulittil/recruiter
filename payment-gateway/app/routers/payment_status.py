"""
Роутеры для проверки статуса платежей и синхронизации.
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..database import get_session
from ..models import Payment, SelfEmployedReceipt
from ..schemas import PaymentDTO
from ..services.receipt_service import ReceiptService
from ..payment_providers.selfwork import SelfworkProvider
from ..payment_providers.robokassa import RobokassaProvider

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/payments/{payment_id}/complete")
async def complete_payment_and_create_receipt(
    payment_id: int,
    session: AsyncSession = Depends(get_session)
):
    """
    Завершить платеж и создать чек самозанятого.
    
    Вызывается после успешной оплаты через платежную систему.
    """
    result = await session.execute(
        select(Payment).where(Payment.payment_id == payment_id)
    )
    payment = result.scalar_one_or_none()
    
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Платеж не найден"
        )
    
    if payment.status == "completed":
        return {"status": "already_completed", "message": "Платеж уже завершен"}
    
    if payment.payment_type != "legal_entity":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Этот endpoint предназначен только для платежей от юридических лиц"
        )
    
    try:
        payment.status = "completed"
        
        metadata = payment.payment_metadata or {}
        company_info = metadata.get("company_info", {})
        
        receipt_service = ReceiptService()
        receipt = await receipt_service.create_receipt(
            session=session,
            payment=payment,
            client_name=company_info.get("name", "Клиент"),
            client_type="legal_entity",
            client_inn=company_info.get("inn"),
            service_name="Услуги по подбору персонала",
            email=company_info.get("email"),
            phone=company_info.get("phone")
        )
        
        payment.receipt_id = receipt.receipt_id
        
        await session.commit()
        await session.refresh(payment)
        await session.refresh(receipt)
        
        logger.info(f"Payment completed and receipt created: payment_id={payment_id}, receipt_id={receipt.receipt_id}")
        
        return {
            "status": "success",
            "payment_id": payment_id,
            "receipt_id": receipt.receipt_id,
            "receipt_number": receipt.receipt_number,
            "receipt_url": receipt.receipt_url,
            "message": "Платеж завершен, чек создан"
        }
        
    except Exception as e:
        logger.error(f"Error completing payment: {e}", exc_info=True)
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при завершении платежа: {str(e)}"
        )


@router.post("/payments/{payment_id}/sync-status")
async def sync_payment_status(
    payment_id: int,
    session: AsyncSession = Depends(get_session)
):
    """
    Синхронизировать статус платежа с провайдером (Selfwork, Robokassa и т.д.).
    
    Полезно для проверки статуса платежа вручную или по расписанию.
    """
    result = await session.execute(
        select(Payment).where(Payment.payment_id == payment_id)
    )
    payment = result.scalar_one_or_none()
    
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Платеж не найден"
        )
    
    if payment.status == "completed":
        return {
            "status": "already_completed",
            "message": "Платеж уже завершен",
            "payment_id": payment_id
        }
    
    try:
        provider_status = None
        
        if payment.provider == "selfwork" and payment.provider_payment_id:
            provider = SelfworkProvider()
            provider_status = await provider.check_payment_status(payment.provider_payment_id)
        elif payment.provider == "robokassa" and payment.provider_payment_id:
            provider = RobokassaProvider()
            provider_status = await provider.check_payment_status(payment.provider_payment_id)
        else:
            return {
                "status": "not_supported",
                "message": f"Синхронизация статуса не поддерживается для провайдера: {payment.provider}",
                "payment_id": payment_id
            }
        
        if not provider_status or provider_status.get("status") == "unknown":
            return {
                "status": "unknown",
                "message": "Не удалось получить статус от провайдера",
                "payment_id": payment_id,
                "error": provider_status.get("error") if provider_status else "No response"
            }
        
        new_status = provider_status.get("status")
        
        if new_status == "completed" and payment.status != "completed":
            payment.status = "completed"
            
            metadata = payment.payment_metadata or {}
            metadata["provider_status_data"] = provider_status
            payment.payment_metadata = metadata
            
            await session.commit()
            await session.refresh(payment)
            
            if payment.payment_type == "individual":
                try:
                    from ..services.access_service import AccessService
                    access_service = AccessService()
                    await access_service.grant_access_after_payment(
                        session=session,
                        payment=payment
                    )
                except Exception as e:
                    logger.error(f"Failed to grant access after payment sync: {e}", exc_info=True)
            
            logger.info(f"Payment status synced and completed: payment_id={payment_id}")
            return {
                "status": "synced",
                "message": "Статус синхронизирован, платеж завершен",
                "payment_id": payment_id,
                "new_status": "completed"
            }
        elif new_status in ["pending", "processing"]:
            metadata = payment.payment_metadata or {}
            metadata["provider_status_data"] = provider_status
            payment.payment_metadata = metadata
            await session.commit()
            
            return {
                "status": "synced",
                "message": "Статус синхронизирован",
                "payment_id": payment_id,
                "current_status": payment.status,
                "provider_status": new_status
            }
        elif new_status == "failed":
            payment.status = "failed"
            metadata = payment.payment_metadata or {}
            metadata["provider_status_data"] = provider_status
            payment.payment_metadata = metadata
            await session.commit()
            
            return {
                "status": "synced",
                "message": "Статус синхронизирован, платеж не прошел",
                "payment_id": payment_id,
                "new_status": "failed"
            }
        else:
            return {
                "status": "synced",
                "message": "Статус синхронизирован",
                "payment_id": payment_id,
                "current_status": payment.status,
                "provider_status": new_status
            }
            
    except Exception as e:
        logger.error(f"Error syncing payment status: {e}", exc_info=True)
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при синхронизации статуса: {str(e)}"
        )

