"""
Kafka producer для отправки сообщений в bot-core.
"""
import json
import logging
import uuid
from typing import Dict, Any, Optional
from aiokafka import AIOKafkaProducer
from aiokafka.errors import KafkaError
import asyncio

from .config import settings

logger = logging.getLogger(__name__)


class KafkaProducer:
    """Producer для отправки ответов в bot-core через Kafka."""
    
    def __init__(self):
        self._bootstrap_servers = settings.KAFKA_BOOTSTRAP_SERVERS
        self._topic = settings.BOT_RESPONSES_TOPIC
        self._producer: AIOKafkaProducer | None = None
    
    async def start(self):
        """Запустить producer."""
        def serialize_value(v: Any) -> bytes:
            """Сериализовать значение в JSON."""
            if isinstance(v, dict):
                return json.dumps(v, default=str).encode("utf-8")
            return json.dumps(v, default=str).encode("utf-8")
        
        retry_delay = 2
        max_retries = 10
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                self._producer = AIOKafkaProducer(
                    bootstrap_servers=self._bootstrap_servers.split(","),
                    value_serializer=serialize_value,
                    key_serializer=lambda k: k.encode("utf-8") if k else None,
                    request_timeout_ms=10000,
                )
                await self._producer.start()
                logger.info(f"Kafka producer started. Topic: {self._topic}")
                return
            except Exception as e:
                retry_count += 1
                if retry_count < max_retries:
                    logger.warning(
                        f"Failed to start Kafka producer (attempt {retry_count}/{max_retries}): {e}. "
                        f"Retrying in {retry_delay} seconds..."
                    )
                    await asyncio.sleep(retry_delay)
                    retry_delay = min(retry_delay * 1.2, 10)
                    continue
                logger.error(f"Failed to start Kafka producer: {e}", exc_info=True)
                raise
    
    async def stop(self):
        """Остановить producer."""
        if self._producer:
            try:
                await self._producer.stop()
                logger.info("Kafka producer stopped")
            except Exception as e:
                logger.error(f"Error stopping Kafka producer: {e}", exc_info=True)
            finally:
                self._producer = None
    
    async def send_response(self, response: Dict[str, Any]) -> str:
        """Отправить ответ в Kafka."""
        if not self._producer:
            raise RuntimeError("Producer is not started. Call start() first.")
        
        response_id = response.get("response_id", uuid.uuid4().hex)
        
        try:
            key = f"{response.get('company_id', 0)}_{response.get('chat_id', 0)}"
            
            future = self._producer.send(
                self._topic,
                value=response,
                key=key,
            )
            
            record_metadata = await future
            logger.info(
                f"Response sent to Kafka. Response ID: {response_id}, "
                f"Topic: {self._topic}, "
                f"Partition: {record_metadata.partition}, Offset: {record_metadata.offset}"
            )
            
            return response_id
        except KafkaError as e:
            logger.error(f"Kafka error while sending response: {e}", exc_info=True)
            raise
        except Exception as e:
            logger.error(f"Unexpected error while sending response: {e}", exc_info=True)
            raise



    global kafka_producer
    if kafka_producer is None:
        kafka_producer = KafkaProducer()
        await kafka_producer.start()
    return kafka_producer

