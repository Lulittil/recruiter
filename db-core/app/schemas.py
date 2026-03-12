from datetime import datetime
from typing import Optional
from enum import Enum
from pydantic import BaseModel, Field, EmailStr


class UserProfileCreate(BaseModel):
    id: str = Field(..., example="user-123")
    full_name: str
    profile_data: dict = Field(default_factory=dict)


class UserProfileDTO(UserProfileCreate):
    updated_at: datetime | None = Field(default_factory=datetime.utcnow)


