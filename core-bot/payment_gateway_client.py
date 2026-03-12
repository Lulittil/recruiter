"""
Клиент для взаимодействия с Payment Gateway Service.
"""
import logging
from typing import Dict, Any, Optional
import httpx

from config import get_settings

logger = logging.getLogger(__name__)


class PaymentGatewayClient:
    """Клиент для Payment Gateway Service."""
    
    def __init__(self, base_url: Optional[str] = None):
        if base_url is None:
            settings = get_settings()
            base_url = settings.payment_gateway_url
        self.base_url = base_url.rstrip("/")
        self._client: Optional[httpx.AsyncClient] = None
    
    async def connect(self):
        """Подключиться к сервису."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=30.0
            )
            logger.info(f"Payment Gateway client initialized with URL: {self.base_url}")
            

        if not self._client:
            await self.connect()
        
        payload = {
            "user_id": user_id,
            "vacancy_id": vacancy_id,
            "payment_type": payment_type,
            "amount": amount,
            "currency": currency
        }
        
        if company_info:
            payload["company_info"] = company_info
        
        if telegram_data:
            payload["telegram_data"] = telegram_data
        

                    )
                    import asyncio
                    await asyncio.sleep(retry_delay)

        if not self._client:
            await self.connect()
        
        try:
            response = await self._client.get(f"/api/v1/users/{telegram_user_id}/access")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:

        if not self._client:
            await self.connect()
        
        try:
            response = await self._client.post(
                f"/api/v1/users/{telegram_user_id}/increment-offer-analysis",
                json={"count": count}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Error incrementing offer analysis count: {e}")
            raise



    global _payment_gateway_client
    _payment_gateway_client = client

