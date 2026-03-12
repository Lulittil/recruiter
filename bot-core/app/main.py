import asyncio
import logging

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, status

from .producer import CommandProducer
from .schemas import CommandRequest, CommandResponse
from .db_client import DBClient
from .bot_manager import BotManager
from .response_consumer import ResponseConsumer
from .kafka_admin import ensure_topics_exist
from .config import get_settings


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(title="bot-core")
producer = CommandProducer()
db_client = DBClient()
bot_manager: BotManager | None = None
response_consumer: ResponseConsumer | None = None


@app.on_event("startup")
async def startup() -> None:
    global bot_manager, response_consumer
    
    try:
        settings = get_settings()
        
        # Ensure required Kafka topics exist
        required_topics = [
            settings.bot_events_topic,
            settings.bot_responses_topic,
        ]
        logger.info(f"Ensuring Kafka topics exist: {required_topics}")
        await ensure_topics_exist(required_topics, settings.kafka_bootstrap_servers)
        
        # Start Kafka producer (with retry logic)
        await producer.start()
        logger.info("Kafka producer started")
        
        try:
            # Connect to db-core
            await db_client.connect()
            logger.info("DB client connected")
            
            # Get active vacancies
            vacancies = await db_client.get_active_vacancies()
            if not vacancies:
                logger.warning("No active vacancies found")
                return
            
            logger.info(f"Found {len(vacancies)} active vacancies")
            
            # Create response consumer
            async def on_response(response_data: dict) -> None:
                if bot_manager:
                    await bot_manager.send_response(response_data)
            
            response_consumer = ResponseConsumer(on_response)
            # Consumer will retry internally
            await response_consumer.start()
            
            # Start consuming responses in background
            asyncio.create_task(response_consumer.consume_loop())
            
            # Create and start bot manager (pass vacancies, but BotManager still uses company_id internally for backward compatibility)
            bot_manager = BotManager(producer, response_consumer, vacancies, db_client)
            await bot_manager.start_all()
            
            logger.info("bot-core service started successfully")
        except Exception as e:
            logger.error(f"Failed to start bot-core service: {e}", exc_info=True)

    global bot_manager
    
    if not bot_manager:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Bot manager is not initialized"
        )
    
    try:
        vacancy_id = vacancy_data.get("vacancy_id")
        bot_token = vacancy_data.get("bot_token")
        
        if not vacancy_id or not bot_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="vacancy_id and bot_token are required"
            )
        

        vacancy = await db_client.get_company_by_id(vacancy_id)
        if not vacancy:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Vacancy {vacancy_id} not found"
            )
        

    global bot_manager
    
    if not bot_manager:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Bot manager is not initialized"
        )
    
    try:
        success = await bot_manager.stop_bot(vacancy_id)
        
        if success:
            logger.info(f"Successfully stopped bot for vacancy {vacancy_id}")
            return {"status": "ok", "message": f"Bot for vacancy {vacancy_id} stopped successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Bot for vacancy {vacancy_id} is not running"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to stop bot: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to stop bot: {str(e)}"
        )


@app.post("/commands", response_model=CommandResponse)
async def submit_command(cmd: CommandRequest) -> CommandResponse:
    try:
        command_id = await producer.send_command(cmd.dict())
        logger.info(f"Command submitted successfully. Command ID: {command_id}, Type: {cmd.command}")
        return CommandResponse(command_id=command_id)
    except RuntimeError as e:
        logger.error(f"Producer not ready: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Kafka producer is not available",
        )
    except Exception as e:
        logger.error(f"Failed to submit command: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit command to Kafka",
        )


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket) -> None:
    await ws.accept()
    try:
        while True:
            payload = await ws.receive_text()
            await ws.send_json({"echo": payload})
    except WebSocketDisconnect:
        return

