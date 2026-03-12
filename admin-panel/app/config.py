from pydantic_settings import BaseSettings
from typing import List, Optional
from pydantic import Field
import json
import os


def parse_cors_origins(origins_str: Optional[str]) -> List[str]:
    """Парсит CORS_ORIGINS из строки или возвращает дефолт."""
    if not origins_str:
        return ["http://localhost:3000", "http://localhost:5173", "http://localhost:80"]
    
    try:

        origins_str = origins_str.strip().strip("'").strip('"')
        return json.loads(origins_str)
    except (json.JSONDecodeError, TypeError, AttributeError):

        origins_str = origins_str.strip().strip("'").strip('"')
        return [origin.strip() for origin in origins_str.split(",") if origin.strip()]


class Settings(BaseSettings):

    SECRET_KEY: str = Field(
        default="your-secret-key-change-in-production-use-env-variable",
        env="SECRET_KEY"
    )
    ALGORITHM: str = Field(default="HS256", env="ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=60 * 24, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    

    DB_CORE_URL: str = Field(default="http://db-core:8000", env="DB_CORE_URL")
    

    BOT_CORE_URL: str = Field(default="http://bot-core:8000", env="BOT_CORE_URL")
    

    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://recruiter:recruiter@postgres:5432/recruiter",
        env="DATABASE_URL"
    )
    

    PAYMENT_GATEWAY_URL: str = Field(default="http://payment-gateway:8000", env="PAYMENT_GATEWAY_URL")
    

        return parse_cors_origins(self.CORS_ORIGINS_STR)


settings = Settings()


    return settings.get_cors_origins()

