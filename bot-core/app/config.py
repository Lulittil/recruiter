from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    kafka_bootstrap_servers: str = Field("localhost:9092", env="KAFKA_BOOTSTRAP_SERVERS")
    commands_topic: str = Field("bot.commands", env="COMMANDS_TOPIC")
    status_topic: str = Field("bot.status", env="STATUS_TOPIC")
    bot_events_topic: str = Field("bot.events", env="BOT_EVENTS_TOPIC")
    offer_events_topic: str = Field("offer.events", env="OFFER_EVENTS_TOPIC")
    bot_responses_topic: str = Field("bot.responses", env="BOT_RESPONSES_TOPIC")
    db_core_url: str = Field("http://db-core:8000", env="DB_CORE_URL")


@lru_cache
def get_settings() -> Settings:
    return Settings()

