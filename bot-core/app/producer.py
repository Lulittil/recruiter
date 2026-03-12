import json
import logging
import uuid
from typing import Any, Dict

from aiokafka import AIOKafkaProducer
from aiokafka.errors import KafkaError

from .config import get_settings

logger = logging.getLogger(__name__)


class CommandProducer:
    """Продюсер для отправки команд в Kafka."""

    def __init__(self) -> None:
        self._settings = get_settings()
        self._producer: AIOKafkaProducer | None = None

    async def start(self) -> None:
        """Подготовка соединения с Kafka с retry логикой."""
        import asyncio
        
        def serialize_value(v: Any) -> bytes:
            """Serialize value to JSON with proper datetime handling."""
            if isinstance(v, dict):
                
            if hasattr(record_metadata, 'partition') and hasattr(record_metadata, 'offset'):
                logger.info(
                    f"Command sent to Kafka. Command ID: {command_id}, "
                    f"Topic: {self._settings.commands_topic}, "
                    f"Partition: {record_metadata.partition}, Offset: {record_metadata.offset}"
                )
            else:

        if not self._producer:
            raise RuntimeError("Producer is not started. Call start() first.")

        event_id = event.get("event_id", uuid.uuid4().hex)
        

        if topic is None:

            metadata = event.get("metadata", {})
            callback_data = event.get("callback_data", "")
            is_vacancy_analysis = metadata.get("is_vacancy_analysis", False)
            
            if is_vacancy_analysis or (callback_data and callback_data.startswith("analyze_offer_")):
                topic = self._settings.offer_events_topic
            else:
                topic = self._settings.bot_events_topic
        
        try:

            key = f"{event.get('company_id', 0)}_{event.get('chat_id', 0)}"
            

            future = self._producer.send(
                topic,
                value=event,
                key=key,
            )
            


            record_metadata = await future
            

            if hasattr(record_metadata, 'partition') and hasattr(record_metadata, 'offset'):
                logger.debug(
                    f"Bot event sent to Kafka. Event ID: {event_id}, "
                    f"Topic: {topic}, "
                    f"Partition: {record_metadata.partition}, Offset: {record_metadata.offset}"
                )
            else:

                logger.debug(
                    f"Bot event sent to Kafka. Event ID: {event_id}, "
                    f"Topic: {topic}"
                )
            
            return event_id
        except KafkaError as e:
            logger.error(f"Kafka error while sending bot event: {e}", exc_info=True)
            raise
        except Exception as e:
            logger.error(f"Unexpected error while sending bot event: {e}", exc_info=True)
            raise

