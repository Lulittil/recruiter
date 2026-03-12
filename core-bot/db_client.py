"""
HTTP client for db-core service.
"""
import os
from typing import Optional, Any, Dict, List
import httpx
import logging

from config import get_settings

logger = logging.getLogger(__name__)

# Global DB client instance
_db_client_instance: Optional["DBClient"] = None


def get_db_client() -> "DBClient":
    """Get global DB client instance."""
    global _db_client_instance
    if _db_client_instance is None:
        raise RuntimeError("DB client not initialized. Call set_db_client() first.")
    return _db_client_instance


def set_db_client(client: "DBClient") -> None:
    """Set global DB client instance."""
    global _db_client_instance
    _db_client_instance = client


def get_db_core_url() -> str:
    """Get db-core service URL from environment."""
    settings = get_settings()
    db_core_url = settings.db_core_url.strip()
    return db_core_url.rstrip("/")


class DBClient:
    """HTTP client for db-core service."""

    def __init__(self, base_url: Optional[str] = None) -> None:
        self._base_url = base_url or get_db_core_url()
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

    async def get_vacancy(self, vacancy_id: int, owner_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """Get vacancy by ID, optionally checking ownership."""
        assert self._client is not None, "Client is not initialized. Call connect() first."
        try:
            params = {}
            if owner_id is not None:
                params["owner_id"] = owner_id
            response = await self._client.get(f"/vacancies/{vacancy_id}", params=params)
            if response.status_code == 404:
                return None
            if response.status_code == 403:
                raise PermissionError("You don't have access to this vacancy")
            response.raise_for_status()
            return response.json()
        except PermissionError:
            raise
        except Exception as e:
            logger.error(f"Error getting vacancy {vacancy_id}: {e}", exc_info=True)
            return None

    async def get_active_vacancies(self, owner_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get all active vacancies, optionally filtered by owner_id."""
        assert self._client is not None, "Client is not initialized. Call connect() first."
        try:
            params = {}
            if owner_id is not None:
                params["owner_id"] = owner_id
            response = await self._client.get("/vacancies/active", params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting active vacancies: {e}", exc_info=True)
            return []

    async def create_vacancy(self, vacancy_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new vacancy."""
        assert self._client is not None, "Client is not initialized. Call connect() first."
        try:
            response = await self._client.post("/vacancies", json=vacancy_data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error creating vacancy: {e}", exc_info=True)
            raise

    async def update_vacancy(self, vacancy_id: int, vacancy_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a vacancy."""
        assert self._client is not None, "Client is not initialized. Call connect() first."
        try:
            # Include vacancy_id in the data for update
            vacancy_data["vacancy_id"] = vacancy_id
            response = await self._client.post("/vacancies", json=vacancy_data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error updating vacancy {vacancy_id}: {e}", exc_info=True)
            raise

    async def delete_vacancy(self, vacancy_id: int) -> bool:
        """Delete a vacancy (close it)."""
        assert self._client is not None, "Client is not initialized. Call connect() first."
        try:
            # Get vacancy and set is_closed to True
            vacancy = await self.get_vacancy(vacancy_id)
            if not vacancy:
                return False
            
            vacancy["is_closed"] = True
            await self.update_vacancy(vacancy_id, vacancy)
            return True
        except Exception as e:
            logger.error(f"Error deleting vacancy {vacancy_id}: {e}", exc_info=True)
            return False

    async def get_vacancy_managers(self, vacancy_id: int) -> List[Dict[str, Any]]:
        """Get all managers for a vacancy."""
        assert self._client is not None, "Client is not initialized. Call connect() first."
        try:
            response = await self._client.get(f"/vacancy-managers/vacancy/{vacancy_id}")
            if response.status_code == 404:
                return []
            response.raise_for_status()
            data = response.json()
            return data.get("managers", [])
        except Exception as e:
            logger.error(f"Error getting vacancy managers: {e}", exc_info=True)
            return []

    async def add_vacancy_manager(self, vacancy_id: int, manager_chat_id: int) -> Optional[Dict[str, Any]]:
        """Add a manager to a vacancy."""
        assert self._client is not None, "Client is not initialized. Call connect() first."
        try:
            response = await self._client.post(
                "/vacancy-managers",
                json={"vacancy_id": vacancy_id, "manager_chat_id": manager_chat_id}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error adding vacancy manager: {e}", exc_info=True)
            raise

    async def remove_vacancy_manager(self, vacancy_manager_id: int) -> bool:
        """Remove a manager from a vacancy."""
        assert self._client is not None, "Client is not initialized. Call connect() first."
        try:
            response = await self._client.delete(f"/vacancy-managers/{vacancy_manager_id}")
            if response.status_code == 404:
                return False
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Error removing vacancy manager: {e}", exc_info=True)
            return False

    async def set_distribution_strategy(self, vacancy_id: int, strategy: str, owner_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """Set distribution strategy for a vacancy."""
        assert self._client is not None, "Client is not initialized. Call connect() first."
        try:
            params = {"strategy": strategy}
            if owner_id is not None:
                params["owner_id"] = owner_id
            response = await self._client.put(
                f"/vacancies/{vacancy_id}/distribution-strategy",
                params=params
            )
            if response.status_code == 403:
                raise PermissionError("You don't have permission to modify this vacancy")
            response.raise_for_status()
            return response.json()
        except PermissionError:
            raise
        except Exception as e:
            logger.error(f"Error setting distribution strategy: {e}", exc_info=True)
            raise

    async def get_distribution_stats(self, vacancy_id: int) -> Optional[Dict[str, Any]]:
        """Get distribution statistics for a vacancy."""
        assert self._client is not None, "Client is not initialized. Call connect() first."
        try:
            response = await self._client.get(f"/vacancies/{vacancy_id}/distribution-stats")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting distribution stats: {e}", exc_info=True)
            return None

    async def is_user_owner(self, owner_id: int) -> bool:
        """Check if user is owner of at least one vacancy."""
        assert self._client is not None, "Client is not initialized. Call connect() first."
        try:
            # Get active vacancies filtered by owner_id
            response = await self._client.get("/vacancies/active", params={"owner_id": owner_id})
            response.raise_for_status()
            vacancies = response.json()
            return len(vacancies) > 0
        except Exception as e:
            logger.error(f"Error checking if user is owner: {e}", exc_info=True)
            return False

