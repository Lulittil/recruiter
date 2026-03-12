"""
Базовый класс для платежных провайдеров.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from decimal import Decimal


class PaymentProvider(ABC):
    """Базовый класс для платежных провайдеров."""
    
    @abstractmethod
    async def create_payment(
        self,
        amount: Decimal,
        payment_id: int,
        description: str,
        email: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Создать платеж и получить URL для оплаты."""
        pass
    
    @abstractmethod
    async def check_payment_status(
        self,
        provider_payment_id: str
    ) -> Dict[str, Any]:
        """Проверить статус платежа."""
        pass
    
    @abstractmethod
    def verify_payment_signature(
        self,
        amount: Decimal,
        payment_id: int,
        signature: str
    ) -> bool:
        """Проверить подпись платежа (для webhook)."""
        pass

