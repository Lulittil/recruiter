"""
Клиент для взаимодействия с db-core сервисом.
"""
import httpx
import asyncio
import logging
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)


class DBClient:
    """Клиент для работы с db-core API."""
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.client: Optional[httpx.AsyncClient] = None
    
    async def connect(self):
        """Инициализировать HTTP клиент."""
        if self.client is None:
            self.client = httpx.AsyncClient(
                timeout=httpx.Timeout(30.0, connect=10.0),
                limits=httpx.Limits(max_keepalive_connections=10, max_connections=20)
            )
    
    async def close(self):
        """Закрыть HTTP клиент."""
        if self.client:
            try:
                await self.client.aclose()
            except Exception as e:
                logger.warning(f"Error closing HTTP client: {e}")
            finally:
                self.client = None
    
    async def get_manager_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Получить первого менеджера по email (если их несколько, берем первого)."""
        await self.connect()
        
        if not self.client:
            logger.error("HTTP client is not initialized")
            return None
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = await self.client.get(
                    f"{self.base_url}/vacancy-managers/by-email/{email}"
                )
                if response.status_code == 200:
                    manager = response.json()

                    if isinstance(manager, list):
                        return manager[0] if manager else None
                    return manager
                elif response.status_code == 404:
                    return None
                else:
                    logger.error(f"Error getting manager by email: {response.status_code} - {response.text}")
                    return None
            except (httpx.ReadError, httpx.ConnectError, httpx.TimeoutException) as e:
                if attempt < max_retries - 1:
                    logger.warning(f"Retry {attempt + 1}/{max_retries} for get_manager_by_email: {e}")
                    await asyncio.sleep(0.5 * (attempt + 1))

        if not self.client:
            await self.connect()
        
        try:
            response = await self.client.get(f"{self.base_url}/steps-screen/{step_id}")
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                return None
            else:
                logger.error(f"Error getting step screen: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            logger.error(f"Exception getting step screen: {e}", exc_info=True)
            return None



    global _db_client
    if _db_client is None:
        from .config import settings
        _db_client = DBClient(settings.DB_CORE_URL)
    return _db_client

