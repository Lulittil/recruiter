import httpx
import logging
from typing import Optional

from .config import get_settings

logger = logging.getLogger(__name__)


class DBClient:
    """HTTP client for db-core service."""

    def __init__(self, base_url: Optional[str] = None) -> None:
        settings = get_settings()
        self._base_url = base_url or settings.db_core_url
        self._client: Optional[httpx.AsyncClient] = None

    async def connect(self) -> None:
        """Initialize HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self._base_url,
                timeout=30.0,
            )
            logger.info(f"DB client connected to {self._base_url}")

    async def close(self) -> None:
        """Close HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None
            logger.info("DB client closed")

    async def get_active_vacancies(self) -> list[dict]:
        """Get all active vacancies."""
        assert self._client is not None, "Client is not initialized. Call connect() first."
        response = await self._client.get("/vacancies/active")
        response.raise_for_status()
        return response.json()
    
    async def get_company_by_recruiter_chat_id(self, chat_id: int) -> Optional[dict]:
        """Get vacancy by manager chat ID (checks vacancy_managers table)."""
        assert self._client is not None, "Client is not initialized. Call connect() first."
        try:
            # Get all vacancies where this chat_id is a manager
            response = await self._client.get(f"/vacancy-managers/manager/{chat_id}")
            response.raise_for_status()
            managers = response.json()
            
            if not managers:
                logger.warning(f"No vacancies found for manager chat_id={chat_id}")
                return None
            
            # Get the first vacancy (or we could return all, but for backward compatibility return first)
            first_manager = managers[0]
            vacancy_id = first_manager.get("vacancy_id")
            
            if vacancy_id:
                # Get full vacancy details
                vacancy = await self.get_company_by_id(vacancy_id)
                if vacancy:
                    logger.info(f"Found vacancy {vacancy_id} for manager chat_id={chat_id}")
                    return vacancy
            
            logger.warning(f"No vacancy found for manager chat_id={chat_id}")
            return None
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.warning(f"No vacancies found for manager chat_id={chat_id}")
                return None
            raise
        except Exception as e:
            logger.error(f"Error getting vacancy by manager chat_id {chat_id}: {e}", exc_info=True)
            return None
    
    async def get_company_by_id(self, company_id: int) -> Optional[dict]:
        """Get vacancy by ID (backward compatibility - company_id is actually vacancy_id)."""
        assert self._client is not None, "Client is not initialized. Call connect() first."
        try:
            response = await self._client.get(f"/vacancies/{company_id}")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            raise
        except Exception as e:
            logger.error(f"Error getting vacancy by id {company_id}: {e}", exc_info=True)
            return None
    
    async def is_manager_for_company(self, chat_id: int, company_id: int) -> bool:
        """Check if chat_id is a manager for specific vacancy (company_id is actually vacancy_id)."""
        assert self._client is not None, "Client is not initialized. Call connect() first."
        try:
            # First, get all vacancies where this chat_id is a manager
            # This is more efficient and ensures we check the right way
            logger.debug(f"Checking if chat_id={chat_id} is manager for vacancy_id={company_id}")
            
            response = await self._client.get(f"/vacancy-managers/manager/{chat_id}")
            response.raise_for_status()
            manager_vacancies = response.json()
            
            if not manager_vacancies:
                logger.debug(f"User {chat_id} is not a manager for any vacancy")
                return False
            
            # Check if this specific vacancy_id is in the list
            for manager_vacancy in manager_vacancies:
                vacancy_id = manager_vacancy.get("vacancy_id")
                if vacancy_id == company_id:
                    logger.info(f"User {chat_id} is a manager for vacancy {company_id}")
                    return True
            
            logger.debug(f"User {chat_id} is a manager, but not for vacancy {company_id}")
            return False
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.debug(f"No vacancies found for manager chat_id={chat_id}")
                return False
            logger.error(f"HTTP error checking if manager for vacancy: {e}", exc_info=True)
            return False
        except Exception as e:
            logger.error(f"Error checking if manager for vacancy: {e}", exc_info=True)
            return False
    
    async def decrement_offer_count(self, company_id: int) -> Optional[dict]:
        """Decrement count_report_offers for a vacancy."""
        assert self._client is not None, "Client is not initialized. Call connect() first."
        try:
            response = await self._client.post(f"/vacancies/{company_id}/decrement-offer-count")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.warning(f"Vacancy {company_id} not found")
                return None
            elif e.response.status_code == 400:
                logger.warning(f"No offer analysis attempts available for vacancy {company_id}")
                return None
            raise
        except Exception as e:
            logger.error(f"Error decrementing offer count for vacancy {company_id}: {e}", exc_info=True)
            return None

