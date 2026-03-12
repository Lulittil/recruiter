"""
Kafka Admin Client for topic management.
Uses kafka-python's KafkaAdminClient wrapped in run_in_executor for async operations.
"""
import asyncio
import logging
from typing import List
from concurrent.futures import ThreadPoolExecutor

from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError

from .config import get_settings

logger = logging.getLogger(__name__)

_executor = ThreadPoolExecutor(max_workers=2)


async def ensure_topics_exist(topics: List[str], bootstrap_servers: str) -> None:
    """
    Ensure that Kafka topics exist, creating them if necessary.
    
    Args:
        topics: List of topic names to ensure exist
        bootstrap_servers: Kafka bootstrap servers (comma-separated)
    """
    retry_delay = 2
    max_retries = 20
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            # Run in executor to avoid blocking
            await asyncio.get_event_loop().run_in_executor(
                _executor,
                _create_topics_sync,
                topics,
                bootstrap_servers
            )
            logger.info(f"All required topics ensured: {topics}")
            return
            
        except Exception as e:
            retry_count += 1
            error_msg = str(e)
            if retry_count < max_retries:
                logger.warning(
                    f"Failed to ensure topics exist (attempt {retry_count}/{max_retries}): {e}. "
                    f"Retrying in {retry_delay} seconds..."
                )
                await asyncio.sleep(retry_delay)
                retry_delay = min(retry_delay * 1.2, 10)
                continue
            logger.error(f"Failed to ensure topics exist: {e}", exc_info=True)
            raise


def _create_topics_sync(topics: List[str], bootstrap_servers: str) -> None:
    """Synchronous function to create topics."""
    admin_client = None
    try:
        admin_client = KafkaAdminClient(
            bootstrap_servers=bootstrap_servers.split(","),
            client_id='topic-creator',
        )
        
        # Get existing topics
        existing_topics = set(admin_client.list_topics())
        logger.info(f"Existing topics: {existing_topics}")
        
        # Find topics that need to be created
        topics_to_create = [topic for topic in topics if topic not in existing_topics]
        
        if topics_to_create:
            new_topics = [
                NewTopic(
                    name=topic,
                    num_partitions=1,
                    replication_factor=1,
                )
                for topic in topics_to_create
            ]
            try:
                admin_client.create_topics(new_topics=new_topics, validate_only=False)
                logger.info(f"Created topics: {topics_to_create}")
            except TopicAlreadyExistsError:
                # Topic was created between check and creation
                logger.info(f"Topics already exist (race condition): {topics_to_create}")
        else:
            logger.info(f"All required topics already exist: {topics}")
            
    finally:
        if admin_client:
            try:
                admin_client.close()
            except Exception:
                pass

