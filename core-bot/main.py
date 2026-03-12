"""
Main entry point for core-bot service.
"""
import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import get_settings
from db_client import DBClient
from bot_handler import router as bot_router
from payment_handler import router as payment_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)



async def main() -> None:
    """Main function to start core-bot."""
    settings = get_settings()
    
    # Validate bot token
    if not settings.bot_token or not settings.bot_token.strip():
        logger.error("CORE_BOT_TOKEN is not set or is empty!")
        logger.error("Please set CORE_BOT_TOKEN environment variable or add it to .env file")
        logger.error("You can get a bot token from @BotFather in Telegram")
        sys.exit(1)
    
    # Check if default placeholder value is still present
    if settings.bot_token.strip() in ["your_bot_token_here", "YOUR_BOT_TOKEN_HERE"]:
        logger.error("=" * 60)
        logger.error("⚠️  CORE_BOT_TOKEN contains placeholder value!")
        logger.error("=" * 60)
        logger.error("Please replace 'your_bot_token_here' with your actual bot token.")
        logger.error("")
        logger.error("To get a bot token:")
        logger.error("1. Open @BotFather in Telegram")
        logger.error("2. Send /newbot command")
        logger.error("3. Follow the instructions")
        logger.error("4. Copy the token and add it to .env file:")
        logger.error("   CORE_BOT_TOKEN=your_actual_token_here")
        logger.error("")
        logger.error("Example token format: 1234567890:ABCdefGHIjklMNOpqrsTUVwxyz")
        logger.error("=" * 60)
        sys.exit(1)
    
    # Check token format (Telegram bot tokens have format: numbers:letters)
    if ":" not in settings.bot_token or len(settings.bot_token.split(":")) != 2:
        logger.error("=" * 60)
        logger.error("⚠️  Invalid bot token format!")
        logger.error("=" * 60)
        logger.error(f"Received token (first 30 chars): {settings.bot_token[:30]}...")
        logger.error("")
        logger.error("Token should be in format: 'number:letters'")
        logger.error("Example: 1234567890:ABCdefGHIjklMNOpqrsTUVwxyz")
        logger.error("")
        logger.error("Please check your .env file and ensure CORE_BOT_TOKEN is correct.")
        logger.error("You can get a token from @BotFather in Telegram")
        logger.error("=" * 60)
        sys.exit(1)
    
    # Initialize bot
    try:
        bot = Bot(
            token=settings.bot_token.strip(),
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
    except Exception as e:
        logger.error(f"Failed to initialize bot: {e}")
        logger.error("Please check that CORE_BOT_TOKEN is correct")
        logger.error("You can get a new token from @BotFather in Telegram")
        sys.exit(1)
    
    # Initialize dispatcher
    dp = Dispatcher(storage=MemoryStorage())
    
    # Register error handler for better error logging
    # In aiogram 3.x, error handler is called with (event, data) where data is a dict
    async def error_handler(event, data):
        """Global error handler for dispatcher."""
        # Extract exception from data dict
        exception = data.get("exception") if isinstance(data, dict) else data
        logger.error(f"Unhandled error in handler: {exception}", exc_info=True)
        logger.error(f"Event type: {type(event)}")
        logger.error(f"Event: {event}")
        if isinstance(data, dict):
            logger.error(f"Data keys: {list(data.keys())}")
        return True  # Continue processing
    
    # Register error handler using register method
    dp.errors.register(error_handler)
    
    # Register routers
    dp.include_router(bot_router)
    dp.include_router(payment_router)
    
    # Initialize DB client
    db_client = DBClient()
    await db_client.connect()
    
    # Make db_client available to handlers via global instance
    from db_client import set_db_client
    set_db_client(db_client)
    
    # Initialize Payment Gateway client
    try:
        from payment_gateway_client import PaymentGatewayClient, set_payment_gateway_client
        payment_gateway_url = settings.payment_gateway_url if hasattr(settings, 'payment_gateway_url') else "http://payment-gateway:8000"
        logger.info(f"Initializing Payment Gateway client with URL: {payment_gateway_url}")
        payment_gateway_client = PaymentGatewayClient()
        await payment_gateway_client.connect()
        set_payment_gateway_client(payment_gateway_client)
        logger.info("Payment Gateway client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Payment Gateway client: {e}", exc_info=True)
        logger.warning("Core-bot will continue, but payment features may not work")

    
    try:
        logger.info("Starting core-bot...")
        # Log only first part of token for security
        token_parts = settings.bot_token.split(":")
        if len(token_parts) == 2:
            logger.info(f"Bot token: {token_parts[0]}:***")
        logger.info(f"DB Core URL: {settings.db_core_url}")
        logger.info(f"Test mode: {'Enabled 🧪' if settings.is_test else 'Disabled'}")
        logger.info(f"Admin chat IDs: {settings.admin_chat_ids if settings.admin_chat_ids else 'Not set'}")
        
        # Start polling
        await dp.start_polling(bot)
        
    except KeyboardInterrupt:
        logger.info("Stopping core-bot...")
    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        sys.exit(1)
    finally:
        # Cleanup
        await db_client.close()
        try:
            from payment_gateway_client import get_payment_gateway_client
            payment_gateway = get_payment_gateway_client()
            if payment_gateway:
                await payment_gateway.disconnect()
        except:
            pass
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Core-bot stopped")

