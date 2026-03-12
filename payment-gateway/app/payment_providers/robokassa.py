"""
Интеграция с Robokassa.
"""
import hashlib
import logging
from typing import Dict, Any, Optional
from decimal import Decimal
import httpx

from .base import PaymentProvider
from ..config import get_settings

logger = logging.getLogger(__name__)


class RobokassaProvider(PaymentProvider):
    """Провайдер платежей Robokassa."""
    
    def __init__(self):
        settings = get_settings()
        self.merchant_login = settings.robokassa_merchant_login
        self.password1 = settings.robokassa_password1
        self.password2 = settings.robokassa_password2
        self.is_test = settings.robokassa_is_test
        
        if not all([self.merchant_login, self.password1, self.password2]):
            logger.warning("Robokassa credentials not configured")
    
    def _generate_signature(
        self,
        amount: Decimal,
        invoice_id: int,
        password: str
    ) -> str:
        """Генерация подписи для Robokassa."""
        signature_string = f"{self.merchant_login}:{amount}:{invoice_id}:{password}"
        return hashlib.md5(signature_string.encode()).hexdigest()
    
    async def create_payment(
        self,
        amount: Decimal,
        payment_id: int,
        description: str,
        email: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Создать платеж в Robokassa."""
        if not all([self.merchant_login, self.password1]):
            raise ValueError("Robokassa credentials not configured")
        

        signature = self._generate_signature(amount, payment_id, self.password1)
        

        params = {
            "MerchantLogin": self.merchant_login,
            "OutSum": str(amount),
            "InvId": payment_id,
            "Description": description,
            "SignatureValue": signature,
        }
        
        if self.is_test:
            params["IsTest"] = "1"
        
        if email:
            params["Email"] = email
        

        if kwargs.get("generate_receipt"):
            params["Receipt"] = self._generate_receipt(
                amount=amount,
                items=kwargs.get("items", []),
                sno=kwargs.get("sno", "usn_income")  