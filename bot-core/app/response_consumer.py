import json
import logging
from typing import Callable, Optional, Awaitable
from aiokafka import AIOKafkaConsumer
from aiokafka.errors import KafkaError

from .config import get_settings
from .schemas import BotResponse

logger = logging.getLogger(__name__)


class ResponseConsumer:
    """Consumer for bot responses from hr-bot."""

    def __init__(self, on_response: Callable[[dict], Awaitable[None]]) -> None:
        self._settings = get_settings()
        self._consumer: Optional[AIOKafkaConsumer] = None
        self._on_response = on_response
        self._running = False

    async def start(self) -> None:
        """Start consuming responses with retry logic."""
        import asyncio
        from aiokafka.errors import KafkaError as AIOKafkaError
        
        # Initial delay to let Kafka fully initialize
        await asyncio.sleep(5)
        
        retry_delay = 3
        max_retries = 40  # ~2 minutes total
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                self._consumer = AIOKafkaConsumer(
                    self._settings.bot_responses_topic,
                    bootstrap_servers=self._settings.kafka_bootstrap_servers.split(","),
                    value_deserializer=lambda v: json.loads(v.decode("utf-8")),
                    group_id="bot-core-responses",
                    auto_offset_reset="earliest",
                    request_timeout_ms=15000,
                    session_timeout_ms=30000,
                    heartbeat_interval_ms=3000,
                )
                await self._consumer.start()
                self._running = True
                logger.info(f"Response consumer started. Topic: {self._settings.bot_responses_topic}")
                return
            except (AIOKafkaError, Exception) as e:
                retry_count += 1
                error_msg = str(e)
                # Check for coordinator errors
                if any(err in error_msg for err in [
                    "GroupCoordinatorNotAvailableError", 
                    "15", 
                    "CoordinatorNotAvailable",
                    "NotCoordinator"
                ]):
                    if retry_count < max_retries:
                        logger.warning(
                            f"Kafka coordinator not available (attempt {retry_count}/{max_retries}). "
                            f"Retrying in {retry_delay} seconds..."
                        )
                        await asyncio.sleep(retry_delay)
                        retry_delay = min(retry_delay * 1.15, 8)  # Exponential backoff, max 8s
                        continue
                logger.error(f"Failed to start response consumer: {e}", exc_info=True)
                raise

    async def stop(self) -> None:
        """Stop consuming responses."""
        self._running = False
        if self._consumer:
            try:
                await self._consumer.stop()
                logger.info("Response consumer stopped")
            except Exception as e:
                logger.error(f"Error stopping response consumer: {e}", exc_info=True)
            finally:
                self._consumer = None

    async def consume_loop(self) -> None:
        """Main consumption loop."""
        if not self._consumer:
            raise RuntimeError("Consumer is not started. Call start() first.")
        
        try:
            async for message in self._consumer:
                if not self._running:
                    break
                
                try:
                    response_data = message.value
                    logger.debug(
                        f"Received response: response_id={response_data.get('response_id')}, "
                        f"response_type={response_data.get('response_type')}, "
                        f"parse_mode={response_data.get('parse_mode')}"
                    )
                    await self._on_response(response_data)
                except Exception as e:
                    logger.error(f"Error processing response: {e}", exc_info=True)
        except KafkaError as e:
            logger.error(f"Kafka error in consume loop: {e}", exc_info=True)
            raise
        except Exception as e:
            logger.error(f"Unexpected error in consume loop: {e}", exc_info=True)
            raise

