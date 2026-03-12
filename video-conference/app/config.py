from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):

    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://recruiter:recruiter@postgres:5432/recruiter",
        env="DATABASE_URL"
    )
    

    TRANSCRIPTS_DIR: str = Field(default="/app/transcripts", env="TRANSCRIPTS_DIR")
    

    DB_CORE_URL: str = Field(default="http://db-core:8000", env="DB_CORE_URL")
    

    KAFKA_BOOTSTRAP_SERVERS: str = Field(default="kafka:9092", env="KAFKA_BOOTSTRAP_SERVERS")
    BOT_RESPONSES_TOPIC: str = Field(default="bot.responses", env="BOT_RESPONSES_TOPIC")
    
    # DeepSeek API key
    DEEPSEEK_API_KEY: str = Field(default="", env="DEEPSEEK_API_KEY")
    

        import json
        try:
            origins_str = self.CORS_ORIGINS_STR.strip().strip("'").strip('"')
            return json.loads(origins_str)
        except (json.JSONDecodeError, TypeError, AttributeError):
            return ["http://localhost:3001", "http://localhost:5173"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

