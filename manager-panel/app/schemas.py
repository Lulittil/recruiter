"""
Pydantic схемы для менеджерской панели.
"""
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


class ManagerLogin(BaseModel):
    """Схема для входа менеджера."""
    email: EmailStr
    password: str


class Token(BaseModel):
    """Схема токена."""
    access_token: str
    token_type: str = "bearer"


class ManagerInfo(BaseModel):
    """Информация о менеджере."""
    vacancy_manager_id: int
    vacancy_id: int
    manager_chat_id: int
    email: Optional[str] = None
    created_at: datetime


class CandidateListItem(BaseModel):
    """Кандидат для списка."""
    applicant_id: int
    full_name: Optional[str] = None
    telegram_id: int
    phone_number: Optional[str] = None
    vacancy_id: Optional[int] = None
    date_consent: Optional[datetime] = None
    is_sended: bool
    resume: Optional[str] = None
    step_screen_id: Optional[int] = None
    assigned_manager_id: Optional[int] = None
    final_manager_id: Optional[int] = None

    vacancy_name: Optional[str] = None
    step_screen_name: Optional[str] = None
    primary_analysis: Optional[str] = None  