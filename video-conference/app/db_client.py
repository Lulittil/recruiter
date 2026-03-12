"""
HTTP клиент для взаимодействия с db-core API.
"""
import logging
from typing import Optional, Dict, Any, List
import httpx

from .config import settings

logger = logging.getLogger(__name__)


class DBClient:
    """Клиент для db-core сервиса."""
    
    def __init__(self, base_url: Optional[str] = None):
        if base_url is None:
            base_url = settings.DB_CORE_URL
        self.base_url = base_url.rstrip("/")
        self._client: Optional[httpx.AsyncClient] = None
    
    async def connect(self):
        """Подключиться к сервису."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=30.0
            )
            logger.info(f"DB client initialized with URL: {self.base_url}")
    
    async def close(self):
        """Отключиться от сервиса."""
        if self._client:
            await self._client.aclose()
            self._client = None
            logger.info("DB client closed")
    
    async def get_manager_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Получить менеджера по email."""
        if not self._client:
            await self.connect()
        
        try:
            response = await self._client.get(f"/vacancy-managers/by-email/{email}")
            if response.status_code == 404:
                return None
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            logger.error(f"HTTP error getting manager by email: {e}", exc_info=True)
            raise
        except Exception as e:
            logger.error(f"Error getting manager by email: {e}", exc_info=True)
            raise
    
    async def get_vacancy(self, vacancy_id: int) -> Optional[Dict[str, Any]]:
        """Получить информацию о вакансии."""
        if not self._client:
            await self.connect()
        
        try:
            response = await self._client.get(f"/vacancies/{vacancy_id}")
            if response.status_code == 404:
                return None
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            logger.error(f"HTTP error getting vacancy: {e}", exc_info=True)
            raise
        except Exception as e:
            logger.error(f"Error getting vacancy: {e}", exc_info=True)
            raise
    
    async def get_deepseek_token(self, vacancy_id: int) -> Optional[str]:
        """Получить DeepSeek API токен для вакансии."""
        vacancy = await self.get_vacancy(vacancy_id)
        if vacancy:
            return vacancy.get("deepseek_token")
        return None
    
    async def get_managers_for_vacancy(self, vacancy_id: int) -> List[Dict[str, Any]]:
        """Получить список менеджеров для вакансии."""
        if not self._client:
            await self.connect()
        
        try:
            response = await self._client.get(f"/vacancy-managers/vacancy/{vacancy_id}")
            response.raise_for_status()
            data = response.json()
            return data.get("managers", [])
        except Exception as e:
            logger.error(f"Error getting managers for vacancy: {e}", exc_info=True)
            raise



    global db_client
    if db_client is None:
        db_client = DBClient()
        await db_client.connect()
    return db_client

