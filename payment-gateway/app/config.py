"""
Конфигурация Payment Gateway Service.
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """Настройки сервиса."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Database
    database_url: str = Field(
        default="postgresql+asyncpg://recruiter:recruiter@postgres:5432/recruiter",
        validation_alias="DATABASE_URL",
        description="Database connection URL"
    )
    
    # Robokassa
    robokassa_merchant_login: Optional[str] = Field(
        default=None,
        validation_alias="ROBOKASSA_MERCHANT_LOGIN",
        description="Robokassa merchant login"
    )
    robokassa_password1: Optional[str] = Field(
        default=None,
        validation_alias="ROBOKASSA_PASSWORD1",
        description="Robokassa password 1"
    )
    robokassa_password2: Optional[str] = Field(
        default=None,
        validation_alias="ROBOKASSA_PASSWORD2",
        description="Robokassa password 2"
    )
    robokassa_is_test: bool = Field(
        default=True,
        validation_alias="ROBOKASSA_IS_TEST",
        description="Robokassa test mode"
    )
    

    )
    

    )
    

    )
    

    )
    

    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings

