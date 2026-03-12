"""
Роутеры для обработки webhook от платежных систем.
"""
import logging
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_session
from ..models import Payment
from ..payment_providers.robokassa import RobokassaProvider
from ..payment_providers.selfwork import SelfworkProvider
from ..services.receipt_service import ReceiptService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/webhooks/robokassa")
async def robokassa_webhook(
    request: Request,
    session: AsyncSession = Depends(get_session)
):
    """Обработка webhook от Robokassa."""
    from sqlalchemy import select
    
    form_data = await request.form()
    out_sum = form_data.get("OutSum")
    inv_id = form_data.get("InvId")
    signature = form_data.get("SignatureValue")
    
    if not all([out_sum, inv_id, signature]):
        logger.error("Missing required parameters in Robokassa webhook")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Отсутствуют обязательные параметры"
        )
    
    try:
        payment_id = int(inv_id)
        amount = float(out_sum)
        
        result = await session.execute(
            select(Payment).where(Payment.payment_id == payment_id)
        )
        payment = result.scalar_one_or_none()
        
        if not payment:
            logger.error(f"Payment not found: payment_id={payment_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Платеж не найден"
            )
        
        provider = RobokassaProvider()
        if not provider.verify_payment_signature(
            amount=Decimal(amount),
            payment_id=payment_id,
            signature=signature
        ):
            logger.error(f"Invalid signature for payment: payment_id={payment_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Неверная подпись"
            )
        
        if payment.status != "completed":
            payment.status = "completed"
            
            if payment.payment_type == "legal_entity" and not payment.receipt_id:
                try:
                    receipt_service = ReceiptService()
                    
                    metadata = payment.payment_metadata or {}
                    company_info = metadata.get("company_info", {})
                    
                    if company_info:
                        tariff_id = company_info.get("tariff_id")
                        if tariff_id:
                            service_name = f"Тариф: {company_info.get('tariff_name', 'Тариф')}"
                        else:
                            service_name = "Услуги по подбору персонала"
                        
                        receipt = await receipt_service.create_receipt(
                            session=session,
                            payment=payment,
                            client_name=company_info.get("name", "Клиент"),
                            client_type="legal_entity",
                            client_inn=company_info.get("inn"),
                            service_name=service_name,
                            email=company_info.get("email"),
                            phone=company_info.get("phone")
                        )
                        
                        payment.receipt_id = receipt.receipt_id
                        
                        from ..services.income_service import IncomeService
                        income_service = IncomeService()
                        await income_service.update_income(
                            session=session,
                            amount=payment.amount,
                            client_type="legal_entity"
                        )
                        
                        logger.info(f"Receipt created automatically: receipt_id={receipt.receipt_id}")
                    else:
                        logger.warning(f"Company info not found in payment payment_metadata: payment_id={payment_id}")
                except Exception as e:
                    logger.error(f"Failed to create receipt automatically: {e}", exc_info=True)
            
            await session.commit()
            logger.info(f"Payment completed: payment_id={payment_id}, amount={amount}")
        
        return f"OK{inv_id}"
        
    except ValueError as e:
        logger.error(f"Invalid payment data: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверные данные платежа"
        )
    except Exception as e:
        logger.error(f"Error processing Robokassa webhook: {e}", exc_info=True)
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при обработке webhook"
        )


@router.post("/webhooks/selfwork")
async def selfwork_webhook(
    request: Request,
    session: AsyncSession = Depends(get_session)
):
    """Обработка webhook от Selfwork."""
    from sqlalchemy import select
    from decimal import Decimal
    import json
    
    try:
        content_type = request.headers.get("content-type", "")
        
        if "application/json" in content_type:
            data = await request.json()
        else:
            form_data = await request.form()
            data = dict(form_data)
        
        payment_id = data.get("payment_id") or data.get("order_id") or data.get("inv_id")
        amount = data.get("amount") or data.get("sum")
        status = data.get("status") or data.get("state")
        signature = data.get("signature") or data.get("sign")
        
        if not payment_id:
            logger.error("Missing payment_id in Selfwork webhook")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Отсутствует payment_id"
            )
        
        try:
            payment_id_int = int(payment_id)
            amount_decimal = Decimal(str(amount)) if amount else None
        except (ValueError, TypeError) as e:
            logger.error(f"Invalid payment data: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Неверные данные платежа"
            )
        
        result = await session.execute(
            select(Payment).where(Payment.payment_id == payment_id_int)
        )
        payment = result.scalar_one_or_none()
        
        if not payment:
            logger.error(f"Payment not found: payment_id={payment_id_int}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Платеж не найден"
            )
        
        if signature:
            provider = SelfworkProvider()
            if amount_decimal and not provider.verify_payment_signature(
                amount=amount_decimal,
                payment_id=payment_id_int,
                signature=signature
            ):
                logger.error(f"Invalid signature for payment: payment_id={payment_id_int}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Неверная подпись"
                )
        
        if status in ["paid", "success", "completed"]:
            if payment.status != "completed":
                payment.status = "completed"
                
                metadata = payment.payment_metadata or {}
                metadata["selfwork_data"] = data
                payment.payment_metadata = metadata
                
                logger.info(f"Selfwork payment completed: payment_id={payment_id_int}, amount={amount}")
                
                await session.commit()
                
                try:
                    from ..services.access_service import AccessService
                    access_service = AccessService()
                    await access_service.grant_access_after_payment(
                        session=session,
                        payment=payment
                    )
                except Exception as e:
                    logger.error(f"Failed to grant access after payment: {e}", exc_info=True)
                
                return {"status": "ok", "message": "Payment processed"}
        
        elif status in ["failed", "cancelled", "rejected"]:
            if payment.status != "failed":
                payment.status = "failed"
                await session.commit()
                logger.info(f"Selfwork payment failed: payment_id={payment_id_int}")
                return {"status": "ok", "message": "Payment marked as failed"}
        
        else:
            logger.info(f"Selfwork payment status: {status} for payment_id={payment_id_int}")
            return {"status": "ok", "message": "Payment status updated"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing Selfwork webhook: {e}", exc_info=True)
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при обработке webhook"
        )

