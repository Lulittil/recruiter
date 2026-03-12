import asyncio
import logging
import uuid
from typing import Dict, Optional, Tuple
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.exceptions import TelegramBadRequest, TelegramNetworkError

from .producer import CommandProducer
from .schemas import BotEvent, BotEventType
from .response_consumer import ResponseConsumer

logger = logging.getLogger(__name__)


class BotManager:
    """Manages Telegram bots for all companies."""

    def __init__(
        self,
        producer: CommandProducer,
        response_consumer: ResponseConsumer,
        companies: list[dict],  # Actually vacancies, but keep name for backward compatibility
        db_client=None,
    ) -> None:
        self._producer = producer
        self._response_consumer = response_consumer
        self._companies = companies  # Actually vacancies
        self._db_client = db_client
        self._bots: Dict[int, Bot] = {}
        self._dispatchers: Dict[int, Dispatcher] = {}
        self._tasks: list[asyncio.Task] = []
        self._bot_tasks: Dict[int, asyncio.Task] = {}  # Map vacancy_id -> polling task
        self._token_to_primary_vacancy: Dict[str, int] = {}  # Map bot_token -> primary vacancy_id
        # State for managers waiting for vacancy: {chat_id: vacancy_id}
        self._managers_waiting_vacancy: Dict[int, int] = {}

    async def start_all(self) -> None:
        """Start all bots for all vacancies.
        Groups vacancies by bot_token to avoid conflicts when multiple vacancies use the same token.
        """

        vacancies_by_token: Dict[str, list] = {}
        for vacancy in self._companies:
            bot_token = vacancy["bot_token"]
            if not bot_token:
                logger.warning(f"Vacancy {vacancy.get('vacancy_id')} has no bot_token, skipping")
                continue
            if bot_token not in vacancies_by_token:
                vacancies_by_token[bot_token] = []
            vacancies_by_token[bot_token].append(vacancy)
        

        for bot_token, vacancies in vacancies_by_token.items():
            if len(vacancies) > 1:
                logger.warning(
                    f"Found {len(vacancies)} vacancies with the same bot_token. "
                    f"Using first vacancy (id={vacancies[0]['vacancy_id']}) for bot instance. "
                    f"Other vacancies: {[v['vacancy_id'] for v in vacancies[1:]]}"
                )
            

            primary_vacancy = vacancies[0]
            company_id = primary_vacancy["vacancy_id"]
            
            try:
                bot = Bot(token=bot_token)
                dp = Dispatcher()
                

                for vacancy in vacancies:
                    vac_id = vacancy["vacancy_id"]
                    dp.message.register(
                        self._make_on_start(vac_id), CommandStart()
                    )
                    dp.message.register(
                        self._make_on_withdraw_consent(vac_id), Command("withdraw_consent")
                    )
                    dp.message.register(
                        self._make_on_menu(vac_id), Command("menu")
                    )
                    dp.message.register(
                        self._make_on_message(vac_id), F.text
                    )
                    dp.message.register(
                        self._make_on_message(vac_id), F.document
                    )
                    dp.message.register(
                        self._make_on_message(vac_id), F.photo
                    )
                    dp.callback_query.register(
                        self._make_on_callback(vac_id), F.data
                    )
                
                await bot.delete_webhook(drop_pending_updates=True)
                

                self._bots[company_id] = bot
                self._dispatchers[company_id] = dp
                

                for vacancy in vacancies:
                    vac_id = vacancy["vacancy_id"]
                    if vac_id != company_id:

                        self._bots[vac_id] = bot
                        self._dispatchers[vac_id] = dp
                

                task = asyncio.create_task(
                    self._poll_with_retry(dp, bot, company_id)
                )
                self._tasks.append(task)
                self._bot_tasks[company_id] = task

        company_id = vacancy["vacancy_id"]
        bot_token = vacancy["bot_token"]
        

        if bot_token in self._token_to_primary_vacancy:
            primary_vacancy_id = self._token_to_primary_vacancy[bot_token]
            if primary_vacancy_id != company_id:
                logger.info(
                    f"Bot with token {bot_token[:10]}... is already running for vacancy {primary_vacancy_id}. "
                    f"Reusing existing bot instance for vacancy {company_id}."
                )

                existing_bot = self._bots.get(primary_vacancy_id)
                existing_dp = self._dispatchers.get(primary_vacancy_id)
                if existing_bot and existing_dp:
                    self._bots[company_id] = existing_bot
                    self._dispatchers[company_id] = existing_dp

                    existing_dp.message.register(
                        self._make_on_start(company_id), CommandStart()
                    )
                    existing_dp.message.register(
                        self._make_on_withdraw_consent(company_id), Command("withdraw_consent")
                    )
                    existing_dp.message.register(
                        self._make_on_menu(company_id), Command("menu")
                    )
                    existing_dp.message.register(
                        self._make_on_message(company_id), F.text
                    )
                    existing_dp.message.register(
                        self._make_on_message(company_id), F.document
                    )
                    existing_dp.message.register(
                        self._make_on_message(company_id), F.photo
                    )
                    existing_dp.callback_query.register(
                        self._make_on_callback(company_id), F.data
                    )
                    logger.info(f"Registered handlers for vacancy {company_id} on existing bot")
                    return True
        

        if company_id in self._bots:
            logger.warning(f"Bot for company {company_id} is already running, stopping it first...")
            await self.stop_bot(company_id)

            await asyncio.sleep(2)
        
        try:
            bot = Bot(token=bot_token)
            dp = Dispatcher()
            
            
            event_dict = event.model_dump(mode='json')
            await self._producer.send_bot_event(event_dict)
            logger.debug(f"Sent event {event.event_id} to Kafka")
        except Exception as e:
            logger.error(f"Failed to send event to Kafka: {e}", exc_info=True)

    def _make_on_start(self, company_id: int):
        async def on_start(message: Message) -> None:
            # Use chat_id from the message, not from database
            # This ensures menu is sent to the chat where command was issued
            chat_id = message.chat.id
            
            logger.info(f"Start command received from chat_id={chat_id} for company_id={company_id}")
            
            # Check if user is a manager for THIS specific company (the one that received the command)
            # Always use company_id from the command to ensure dialog continues in the same bot
            is_manager = await self._is_manager_for_company(chat_id, company_id)
            
            if is_manager:
                # If user is manager for this company, send manager menu to the chat where command was issued
                # Always use company_id from the command to ensure response comes from the same bot
                logger.info(f"Sending manager menu to chat_id={chat_id} (from message) for company_id={company_id}")
                await self._send_manager_menu(company_id, chat_id)
                return
            
            # For regular users, send event to hr-bot
            logger.info(f"Sending start event to hr-bot for chat_id={chat_id}, company_id={company_id}")
            event = BotEvent(
                event_id=str(uuid.uuid4()),
                event_type=BotEventType.command,
                company_id=company_id,
                chat_id=chat_id,
                user_id=message.from_user.id if message.from_user else 0,
                username=message.from_user.username if message.from_user else None,
                command="start",
                metadata={"message_id": message.message_id},
            )
            await self._send_event(event)
        
        return on_start

    def _make_on_withdraw_consent(self, company_id: int):
        async def on_withdraw_consent(message: Message) -> None:
            event = BotEvent(
                event_id=str(uuid.uuid4()),
                event_type=BotEventType.command,
                company_id=company_id,
                chat_id=message.chat.id,
                user_id=message.from_user.id if message.from_user else 0,
                username=message.from_user.username if message.from_user else None,
                command="withdraw_consent",
                metadata={"message_id": message.message_id},
            )
            await self._send_event(event)
        
        return on_withdraw_consent

    def _make_on_menu(self, company_id: int):
        async def on_menu(message: Message) -> None:
            # Use chat_id from the message, not from database
            # This ensures menu is sent to the chat where command was issued
            chat_id = message.chat.id
            
            logger.info(f"Menu command received from chat_id={chat_id} for company_id={company_id}")
            
            # Check if user is a manager for THIS specific company (the one that received the command)
            # Always use company_id from the command to ensure dialog continues in the same bot
            is_manager = await self._is_manager_for_company(chat_id, company_id)
            
            logger.info(
                f"Manager check result: is_manager={is_manager}, "
                f"requested_company_id={company_id}"
            )
            
            if is_manager:
                # If user is manager for this company, show menu
                # Always use company_id from the command to ensure response comes from the same bot
                logger.info(f"Sending manager menu to chat_id={chat_id} (from message) for company_id={company_id}")
                await self._send_manager_menu(company_id, chat_id)
            else:

                    )
        
        return on_menu

    def _make_on_message(self, company_id: int):
        async def on_message(message: Message) -> None:
            # Extract message content
            message_text = message.text or message.caption
            
            chat_id = message.chat.id
            
            # Check if manager is waiting for vacancy
            if chat_id in self._managers_waiting_vacancy:
                target_company_id = self._managers_waiting_vacancy[chat_id]
                # Process vacancy submission
                await self._process_vacancy_submission(
                    message, target_company_id, chat_id
                )
                # Remove from waiting state
                del self._managers_waiting_vacancy[chat_id]
                return
            

                # Check if user is a manager for THIS specific company (the one that received the message)
                # Always use company_id from the message to ensure dialog continues in the same bot
                is_manager = await self._is_manager_for_company(chat_id, company_id)
                
                if is_manager:
                    # Check if offer analysis attempts are available
                    vacancy_data = await self._db_client.get_company_by_id(company_id)
                    if not vacancy_data:
                        logger.warning(f"Vacancy {company_id} not found when checking offer count")
                        return
                    
                    count_report_offers = vacancy_data.get("count_report_offers", 0)
                    if count_report_offers <= 0:

                            )
                        return
                    
                    # Always use company_id from the message to ensure response comes from the same bot
                    bot = self._bots.get(company_id)
                    if bot:

                        )
                        # Set state: waiting for vacancy
                        self._managers_waiting_vacancy[chat_id] = company_id
                    return
            
            # For other messages, continue normal processing
            document_id = None
            photo_id = None
            document_content = None
            document_filename = None
            
            bot = self._bots.get(company_id)
            
            # Download document if present
            if message.document and bot:
                try:
                    document_id = message.document.file_id
                    document_filename = message.document.file_name
                    # Download file content
                    file = await bot.get_file(document_id)
                    # Download to bytes
                    import io
                    file_buffer = io.BytesIO()
                    await bot.download(file, destination=file_buffer)
                    document_content = file_buffer.getvalue()
                    logger.debug(f"Downloaded document {document_id}, size: {len(document_content)} bytes")
                except Exception as e:
                    logger.error(f"Error downloading document: {e}", exc_info=True)
                    # Continue without document content
            
            if message.photo and bot:
                try:
                    photo_id = message.photo[-1].file_id  # Get largest photo
                    # For photos, we don't download content as they're usually not resumes
                except Exception as e:
                    logger.error(f"Error getting photo: {e}", exc_info=True)
            
            # Extract user info
            user = message.from_user
            metadata = {
                "message_id": message.message_id,
                "has_document": message.document is not None,
                "has_photo": message.photo is not None,
            }
            if user:
                if user.first_name:
                    metadata["first_name"] = user.first_name
                if user.last_name:
                    metadata["last_name"] = user.last_name
            
            event = BotEvent(
                event_id=str(uuid.uuid4()),
                event_type=BotEventType.message,
                company_id=company_id,
                chat_id=message.chat.id,
                user_id=user.id if user else 0,
                username=user.username if user else None,
                message_text=message_text,
                document_id=document_id,
                photo_id=photo_id,
                document_content=document_content,
                document_filename=document_filename,
                metadata=metadata,
            )
            await self._send_event(event)
        
        return on_message

    def _make_on_callback(self, company_id: int):
        async def on_callback(callback: CallbackQuery) -> None:
            callback_data = callback.data
            chat_id = callback.message.chat.id if callback.message else callback.from_user.id
            
            # Handle analyze_offer callback directly (for managers)
            if callback_data and callback_data.startswith("analyze_offer_"):
                # Check if user is a manager for THIS specific company
                is_manager = await self._is_manager_for_company(chat_id, company_id)
                
                if not is_manager:

                                show_alert=True,
                            )
                    except Exception as e:
                        logger.error(f"Error answering callback: {e}", exc_info=True)
                    return
                
                # Manager confirmed - request vacancy text
                try:
                    bot = self._bots.get(company_id)
                    if bot:

                            show_alert=False,
                        )
                        

                        )
                        # Set state: waiting for vacancy
                        self._managers_waiting_vacancy[chat_id] = company_id
                        logger.info(f"Set waiting state for manager chat_id={chat_id}, company_id={company_id}")
                except Exception as e:
                    logger.error(f"Error processing analyze_offer callback: {e}", exc_info=True)
                return
            
            # For other callbacks, send to hr-bot
            event = BotEvent(
                event_id=str(uuid.uuid4()),
                event_type=BotEventType.callback_query,
                company_id=company_id,
                chat_id=chat_id,
                user_id=callback.from_user.id if callback.from_user else 0,
                username=callback.from_user.username if callback.from_user else None,
                callback_data=callback_data,
                metadata={
                    "callback_query_id": callback.id,
                    "message_id": callback.message.message_id if callback.message else None,
                },
            )
            await self._send_event(event)
        
        return on_callback
    
    async def _is_manager(self, chat_id: int) -> Tuple[bool, Optional[int]]:
        """Check if chat_id is a manager (recruiter) for any company. Returns (is_manager, company_id)."""
        if not self._db_client:
            logger.warning("DB client not available for manager check")
            return False, None
        
        try:
            logger.info(f"Checking if chat_id={chat_id} is a manager")
            company = await self._db_client.get_company_by_recruiter_chat_id(chat_id)
            if company:
                company_id = company.get("company_id")
                logger.info(f"User {chat_id} is a manager for company {company_id}")
                return True, company_id
            logger.info(f"User {chat_id} is not a manager")
            return False, None
        except Exception as e:
            logger.error(f"Error checking if manager: {e}", exc_info=True)
            return False, None
    
    async def _is_manager_for_company(self, chat_id: int, company_id: int) -> bool:
        """Check if chat_id is a manager (recruiter) for specific company."""
        if not self._db_client:
            logger.warning("DB client not available for manager check")
            return False
        
        try:
            logger.info(f"Checking if chat_id={chat_id} is a manager for company_id={company_id}")
            is_manager = await self._db_client.is_manager_for_company(chat_id, company_id)
            logger.info(f"User {chat_id} is manager for company {company_id}: {is_manager}")
            return is_manager
        except Exception as e:
            logger.error(f"Error checking if manager for company: {e}", exc_info=True)
            return False
    
    async def _send_manager_menu(self, company_id: int, chat_id: int) -> None:
        """
        Send manager menu with analyze offer button.
        
        Args:
            company_id: Company ID (actually vacancy_id) to get the bot instance
            chat_id: Chat ID where to send the menu (from message.chat.id, not from DB)
                     This ensures menu is sent to the chat where /start or /menu was issued.
        """
        bot = self._bots.get(company_id)
        if not bot:
            logger.error(f"Bot not found for company {company_id}")
            return
        
        try:
            from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
            
            # Check if offer analysis attempts are available
            vacancy_data = await self._db_client.get_company_by_id(company_id)
            count_report_offers = vacancy_data.get("count_report_offers", 0) if vacancy_data else 0
            

            
            logger.debug(f"Sending manager menu to chat_id={chat_id} for company_id={company_id}")
            await bot.send_message(
                chat_id=chat_id,
                text=menu_text,
                reply_markup=keyboard if keyboard_buttons else None,
            )
        except Exception as e:
            logger.error(f"Error sending manager menu to chat_id={chat_id}: {e}", exc_info=True)

    async def _process_vacancy_submission(
        self, message: Message, company_id: int, chat_id: int
    ) -> None:
        """Process vacancy submission from manager."""
        import base64
        import tempfile
        import os
        
        bot = self._bots.get(company_id)
        if not bot:
            logger.error(f"Bot not found for company {company_id}")
            return
        
        try:
            vacancy_text = None
            error_message = None
            
            # Extract text from message/document
            message_text = message.text or message.caption
            
            if message_text:
                # Check if it's a URL (hh.ru or other)
                if self._looks_like_url(message_text):
                    # Try to extract from URL
                    vacancy_text, error_message = await self._extract_text_from_url(message_text)
                else:
                    # Plain text
                    vacancy_text = message_text
            elif message.document:
                # Download and extract from document
                try:
                    file = await bot.get_file(message.document.file_id)

                )
                return
            

            )
            

                )
    
    def _looks_like_url(self, text: str) -> bool:
        """Check if text looks like a URL."""
        import re
        return bool(re.match(r"^(https?://|www\.)", text, flags=re.IGNORECASE))
    
    async def _extract_text_from_url(self, url: str) -> tuple[str, Optional[str]]:
        """Extract text from URL (hh.ru or other)."""
        try:
            import requests
            from bs4 import BeautifulSoup
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            }
            
            resp = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
            resp.raise_for_status()
            
            soup = BeautifulSoup(resp.text, 'html.parser')
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            text = soup.get_text()


    async def send_response(self, response: dict) -> None:
        """Send response to user via Telegram bot."""
        company_id = response["company_id"]
        chat_id = response["chat_id"]
        response_type = response["response_type"]
        
        bot = self._bots.get(company_id)
        if not bot:
            logger.error(f"Bot not found for company {company_id}")
            return
        
        try:
            if response_type == "text_message":
                reply_markup = None
                if response.get("reply_markup"):
                    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
                    keyboard = []
                    for row in response["reply_markup"].get("inline_keyboard", []):
                        kb_row = []
                        for button in row:
                            kb_row.append(
                                InlineKeyboardButton(
                                    text=button["text"],
                                    callback_data=button["callback_data"]
                                )
                            )
                        keyboard.append(kb_row)
                    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
                
                # Use parse_mode from response if provided, default to None
                parse_mode = response.get("parse_mode")
                
                logger.info(
                    f"Sending text message: company_id={company_id}, chat_id={chat_id}, "
                    f"parse_mode={parse_mode}, text_length={len(response.get('text', ''))}"
                )
                
                await bot.send_message(
                    chat_id=chat_id,
                    text=response["text"],
                    reply_markup=reply_markup,
                    parse_mode=parse_mode,
                )
            
            elif response_type == "document":
                import os
                import tempfile
                import base64
                from aiogram.types import FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton
                
                document_path = response.get("document_path")
                document_content = response.get("document_content")
                document_filename = response.get("document_filename", "document.pdf")
                temp_file_path = None
                
                # If document_content is provided (from hr-bot), save it to temp file
                if document_content:
                    try:
                        # Decode base64 if it's a string (from JSON)
                        if isinstance(document_content, str):
                            file_bytes = base64.b64decode(document_content)
                        elif isinstance(document_content, bytes):
                            file_bytes = document_content
                        else:
                            raise ValueError(f"Unexpected document_content type: {type(document_content)}")
                        
                        
                    # Check if it's an HTML parsing error
                    if isinstance(network_error, TelegramBadRequest) and (
                        "can't parse entities" in error_msg or "unclosed" in error_msg
                    ):
                        # If HTML parsing fails, try sending without parse_mode
                        import re
                        import html as html_module
                        plain_caption = re.sub(r'<[^>]+>', '', response.get("text", ""))
                        plain_caption = html_module.unescape(plain_caption)
                        if len(plain_caption) > 1024:
                            plain_caption = plain_caption[:1021] + "..."
                        try:
                            await bot.send_document(
                                chat_id=chat_id,
                                document=file,
                                caption=plain_caption,
                                reply_markup=reply_markup,
                            )
                        except Exception as retry_error:
                            logger.error(f"Error sending document after HTML fix: {retry_error}", exc_info=True)

                            )
                    else:

                            )
                        else:
                            raise
                finally:
                    # Clean up temp file if it was created from document_content
                    if temp_file_path and os.path.exists(temp_file_path):
                        try:
                            os.remove(temp_file_path)
                            logger.debug(f"Cleaned up temp file: {temp_file_path}")
                        except Exception as e:
                            logger.warning(f"Failed to remove temp file {temp_file_path}: {e}")
            
            elif response_type == "photo":
                from aiogram.types import FSInputFile
                file = FSInputFile(response["photo_path"])
                await bot.send_photo(
                    chat_id=chat_id,
                    photo=file,
                    caption=response.get("text"),
                )
            
            elif response_type == "edit_message":
                reply_markup = None
                if response.get("reply_markup"):
                    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
                    keyboard = []
                    for row in response["reply_markup"].get("inline_keyboard", []):
                        kb_row = []
                        for button in row:
                            kb_row.append(
                                InlineKeyboardButton(
                                    text=button["text"],
                                    callback_data=button["callback_data"]
                                )
                            )
                        keyboard.append(kb_row)
                    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
                

                if response.get("text"):
                    await bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=response["edit_message_id"],
                        text=response["text"],
                        reply_markup=reply_markup,
                    )
                else:

                    await bot.edit_message_reply_markup(
                        chat_id=chat_id,
                        message_id=response["edit_message_id"],
                        reply_markup=reply_markup,
                    )
            
            elif response_type == "answer_callback":
                await bot.answer_callback_query(
                    callback_query_id=response["callback_query_id"],
                    text=response.get("callback_text"),
                    show_alert=False,
                )
            
            elif response_type == "delete_message":
                await bot.delete_message(
                    chat_id=chat_id,
                    message_id=response["delete_message_id"],
                )
            
            response_id = response.get('response_id', 'unknown')
            logger.debug(f"Sent response {response_id} to user")
        
        except TelegramBadRequest as e:
            logger.error(f"Telegram API error: {e}")
        except Exception as e:
            logger.error(f"Failed to send response: {e}", exc_info=True)

