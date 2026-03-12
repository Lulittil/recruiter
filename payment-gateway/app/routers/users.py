"""
Роутеры для работы с пользователями.
"""
import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..database import get_session
from ..models import ActiveUser

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/users/{telegram_user_id}/access")
async def check_user_access(
    telegram_user_id: int,
    session: AsyncSession = Depends(get_session)
) -> dict:
    """
    Проверить доступ пользователя к функциям системы.
    
    Returns:
        dict с информацией о доступе:
        - has_access: bool - есть ли доступ
        - can_create_vacancy: bool - может ли создавать вакансии
        - tariff_id: str - ID текущего тарифа
        - tariff_name: str - название тарифа
        - vacancies_limit: int - лимит вакансий
        - vacancies_used: int - использовано вакансий
        - vacancies_remaining: int - осталось вакансий
        - offer_analyses_limit: int - лимит анализов офферов
        - offer_analyses_used: int - использовано анализов
        - offer_analyses_remaining: int - осталось анализов
    """
    try:

            }
        

            }
        

        )

