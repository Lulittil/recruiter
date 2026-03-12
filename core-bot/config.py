import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """Settings for core-bot service."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Telegram Bot Token (required)
    bot_token: str = Field(..., validation_alias="CORE_BOT_TOKEN", description="Telegram bot token for core-bot")
    
    # Database Core URL
    db_core_url: str = Field(
        default="http://db-core:8000",
        validation_alias="DB_CORE_URL",
        description="URL of db-core service"
    )
    
    # Payment Gateway URL
    payment_gateway_url: str = Field(
        default="http://payment-gateway:8000",
        validation_alias="PAYMENT_GATEWAY_URL",
        description="URL of payment-gateway service"
    )
    
    # Payment settings
    payment_provider_token: Optional[str] = Field(
        default=None,
        validation_alias="PAYMENT_PROVIDER_TOKEN",
        description="Telegram Payment Provider token (from @BotFather)"
    )
    
    # Test mode flag
    is_test: bool = Field(
        default=False,
        validation_alias="IS_TEST",
        description="Enable test mode (disables real payments, uses mock)"
    )
    
    # Admin chat IDs (comma-separated)
    admin_chat_ids: str = Field(
        default="",
        validation_alias="ADMIN_CHAT_IDS",
        description="Comma-separated list of admin chat IDs"
    )
    
    # Allow vacancy creation flag
    is_create: bool = Field(
        default=False,
        validation_alias="IS_CREATE",
        description="Allow vacancy creation (set to true to enable)"
    )
    

    )


_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get settings instance (singleton)."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def get_admin_chat_ids() -> list[int]:
    """Get list of admin chat IDs."""
    settings = get_settings()
    if not settings.admin_chat_ids:
        return []
    
    try:
        return [int(chat_id.strip()) for chat_id in settings.admin_chat_ids.split(",") if chat_id.strip()]
    except ValueError:
        return []

