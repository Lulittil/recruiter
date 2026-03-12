"""
Сервис для генерации чеков самозанятого.
"""
import logging
from datetime import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..models import Payment, SelfEmployedReceipt, IncomeTracking
from ..config import get_settings

logger = logging.getLogger(__name__)


class ReceiptService:
    """Сервис для работы с чеками самозанятого."""
    
    def __init__(self):
        self.settings = get_settings()
        self.inn = self.settings.my_tax_inn


        tax_rate = 6 if client_type == "legal_entity" else 4
        tax_amount = float(payment.amount) * (tax_rate / 100)
        

        receipt_data = None
        receipt_number = None
        
        if self.my_tax_service:
            try:
                receipt_data = await self.my_tax_service.create_receipt(
                    amount=payment.amount,
                    client_name=client_name,
                    client_type=client_type,
                    client_inn=client_inn,
                    service_name=service_name,
                    email=email,
                    phone=phone
                )
                
                if receipt_data:

                logger.info("Will create receipt locally and sync later")
        

        if not receipt_number:
            if self.my_tax_service:
                receipt_number = self.my_tax_service.generate_receipt_number()
            else:

                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                receipt_number = f"RECEIPT-{timestamp}"
            logger.info(f"Generated local receipt number: {receipt_number}")
        

        receipt = SelfEmployedReceipt(
            payment_id=payment.payment_id,
            receipt_number=receipt_number,
            client_name=client_name,
            client_inn=client_inn,
            client_type=client_type,
            amount=payment.amount,
            tax_amount=tax_amount,
            tax_rate=tax_rate,
            status="created"
        )
        

        if receipt_data:
            receipt.receipt_url = receipt_data.get("receipt_url") or receipt_data.get("url")
            receipt.qr_code_url = receipt_data.get("qr_code_url") or receipt_data.get("qr_code")
            receipt.fiscal_data = receipt_data.get("fiscal_data") or {
                "fiscal_drive_number": receipt_data.get("fiscal_drive_number"),
                "fiscal_document_number": receipt_data.get("fiscal_document_number"),
                "fiscal_sign": receipt_data.get("fiscal_sign"),
            }
            receipt.status = "sent"  