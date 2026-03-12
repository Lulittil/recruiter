"""HTTP клиент для взаимодействия с db-core API."""
import httpx
from typing import Optional, List, Dict, Any
from .config import settings
import logging

logger = logging.getLogger(__name__)


class DBCoreClient:
    """Клиент для работы с db-core API."""
    
    def __init__(self):
        self.base_url = settings.DB_CORE_URL.rstrip("/")
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def close(self):
        """Закрыть клиент."""
        await self.client.aclose()
    
    async def _request(self, method: str, endpoint: str, **kwargs) -> Any:
        """Выполнить HTTP запрос."""
        url = f"{self.base_url}{endpoint}"
        try:
            logger.debug(f"Making {method} request to {url} with data: {kwargs.get('json', {})}")
            response = await self.client.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json() if response.content else None
        except httpx.HTTPStatusError as e:
            error_detail = e.response.text if e.response.content else "No error details"
            logger.error(f"HTTP error {e.response.status_code} from {url}: {error_detail}")

            try:
                error_json = e.response.json()
                error_message = error_json.get("detail", error_detail)
            except:
                error_message = error_detail

            from fastapi import HTTPException as FastAPIHTTPException
            raise FastAPIHTTPException(
                status_code=e.response.status_code,
                detail=error_message
            ) from e
        except Exception as e:
            logger.error(f"Request error to {url}: {e}")
            raise
    

        return await self._request("POST", "/vacancies", json={**vacancy_data, "vacancy_id": vacancy_id})
    

        params = {}
        if vacancy_id is not None:
            params["vacancy_id"] = vacancy_id
        return await self._request("PATCH", f"/applicants/telegram/{telegram_id}", json=applicant_data, params=params)
    

        await self._request("DELETE", f"/vacancy-managers/{vacancy_manager_id}")
    

        params = {}
        if vacancy_id is not None:
            params["vacancy_id"] = vacancy_id
        return await self._request("GET", f"/applicants/manager/{manager_chat_id}", params=params)
    

        return await self._request("GET", "/steps-screen")
    

        from .config import settings
        import httpx
        

        bot_core_url = settings.BOT_CORE_URL.rstrip("/")
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{bot_core_url}/bots/start",
                    json=vacancy_data
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error starting bot via bot-core: {e}", exc_info=True)
            raise


# Singleton instance
db_client = DBCoreClient()

