"""
Обработчики команд и сообщений для core-bot.
"""
import logging
from typing import Dict, Any, Optional
import httpx
from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from db_client import DBClient, get_db_client
from payment_gateway_client import PaymentGatewayClient, get_payment_gateway_client
from config import get_settings, get_admin_chat_ids
from tariffs import get_all_tariffs, get_tariff, format_tariff_info
from company_parser import extract_company_info_from_text, verify_company_in_rf_databases
from contract_generator import generate_service_contract

logger = logging.getLogger(__name__)


def get_main_menu() -> ReplyKeyboardMarkup:
    """Create main menu keyboard."""
    settings = get_settings()
    keyboard_buttons = [
        [KeyboardButton(text="📋 Мои вакансии")]
    ]
    

    ])
    
    return ReplyKeyboardMarkup(
        keyboard=keyboard_buttons,
        resize_keyboard=True,
        persistent=True
    )

router = Router()


class VacancyCreationStates(StatesGroup):
    """States for vacancy creation flow."""
    waiting_company_name = State()
    waiting_bot_token = State()
    waiting_openai_token = State()
    waiting_deepseek_token = State()
    waiting_vacancy_description = State()
    waiting_gpt_prompt = State()
    waiting_managers = State()


class ManagerAdditionStates(StatesGroup):
    """States for manager addition flow."""
    waiting_manager_chat_id = State()


class PaymentCompanyInfoStates(StatesGroup):
    """States for collecting company information for legal entity payment."""
    waiting_payment_type = State()  
    """Handle 'Create vacancy' button press."""


        return
    
    try:

            f"{'─' * 30}\n\n"
        )
        
        for idx, vacancy in enumerate(vacancies[:10], 1):  
                text += f"{'─' * 30}\n\n"
        
        
        "owner_id": message.chat.id,  # Set owner_id to user's chat_id
    }
    

        company_name = vacancy.get('company_name', 'Не указано')
        

        try:
            payment_gateway = get_payment_gateway_client()
            increment_result = await payment_gateway.increment_vacancy_count(message.from_user.id)
            if increment_result:
                vacancies_remaining = increment_result.get("vacancies_remaining", 0)
                logger.info(
                    f"Vacancy count incremented for user {message.from_user.id}: "
                    f"remaining={vacancies_remaining}"
                )
        except Exception as e:
            logger.warning(f"Failed to increment vacancy count: {e}")

        return
    
    try:

            return
        
        # Get managers
        managers = await db_client.get_vacancy_managers(vacancy_id)
        
        # Get manager names from Telegram
        manager_info_list = []
        for manager in managers:
            manager_chat_id = manager.get('manager_chat_id')
            try:

            manager_info_list.append((manager_name, manager_chat_id))
        

        company_name = vacancy.get('company_name', 'Не указано')
        is_closed = vacancy.get('is_closed', False)
        status_emoji = "❌" if is_closed else "✅"
        status_text = "Закрыта" if is_closed else "Активна"
        

        return
    
    # Reuse vacancies list logic
    try:

            f"{'─' * 30}\n\n"
        )
        
        for idx, vacancy in enumerate(vacancies[:10], 1):  
                text += f"{'─' * 30}\n\n"
        
        keyboard_buttons = []
        for vacancy in vacancies[:10]:  
            f"{'─' * 30}\n\n"
            f"💡 <b>Выберите действие:</b>"
        )
        
        keyboard_buttons = [
            [InlineKeyboardButton(text="➕ Добавить менеджера", callback_data=f"add_manager_{vacancy_id}")],
        ]
        
        if managers:
            keyboard_buttons.append([
                InlineKeyboardButton(text="🗑️ Удалить менеджера", callback_data=f"remove_managers_{vacancy_id}")
            ])
        
        keyboard_buttons.append([
            InlineKeyboardButton(text="🔙 Назад", callback_data=f"vacancy_{vacancy_id}")
        ])
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
        await callback.message.edit_text(text, reply_markup=keyboard)
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error showing team menu: {e}", exc_info=True)
        await callback.answer("❌ Ошибка", show_alert=True)


@router.callback_query(F.data.startswith("add_manager_"))
async def handle_add_manager(callback: CallbackQuery, state: FSMContext) -> None:
    """Handle add manager callback."""
    if not await is_admin(callback.from_user.id):
        await callback.answer("❌ У вас нет доступа", show_alert=True)
        return
    
    vacancy_id = int(callback.data.split("_")[2])
    await state.update_data(vacancy_id=vacancy_id)
    await state.set_state(ManagerAdditionStates.waiting_manager_chat_id)
    
    await callback.message.answer(
        f"Введите chat_id менеджера для добавления к вакансии 
        text += f"Стратегия: {stats.get('distribution_strategy', 'manual')}\n"
        text += f"Макс. кандидатов: {stats.get('max_candidates_per_manager') or 'Не ограничено'}\n\n"
        text += "Загрузка менеджеров:\n"
        
        managers = stats.get("managers", [])
        if not managers:
            text += "Менеджеры не найдены"
        else:
            for manager in managers:
                chat_id = manager.get("manager_chat_id")
                active_count = manager.get("active_count", 0)
                is_available = manager.get("is_available", True)
                status = "✅" if is_available else "❌"
                max_candidates = manager.get("max_candidates")
                max_text = f" / {max_candidates}" if max_candidates else ""
                
                text += f"{status} Менеджер {chat_id}: {active_count}{max_text} активных кандидатов\n"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="🔙 Назад", callback_data=f"vacancy_{vacancy_id}")
        ]])
        
        await callback.message.edit_text(text, reply_markup=keyboard)
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}", exc_info=True)
        await callback.answer("❌ Ошибка при получении статистики", show_alert=True)


@router.callback_query(F.data.startswith("remove_managers_"))
async def handle_remove_managers_menu(callback: CallbackQuery) -> None:
    """Handle remove managers menu callback - show list of managers to remove."""
    if not await is_admin(callback.from_user.id):
        await callback.answer("❌ У вас нет доступа", show_alert=True)
        return
    
    vacancy_id = int(callback.data.split("_")[2])
    
    try:
        db_client = get_db_client()
    except RuntimeError:
        await callback.answer("❌ Ошибка: DB client не инициализирован", show_alert=True)
        return
    
    try:

            return
        

            return
        
        # Get manager names from Telegram
        manager_info_list = []
        for manager in managers:
            manager_chat_id = manager.get('manager_chat_id')
            vacancy_manager_id = manager.get('vacancy_manager_id')
            try:

        )
        
        keyboard_buttons = []
        for idx, (manager_name, manager_chat_id, vacancy_manager_id) in enumerate(manager_info_list, 1):

        return
    

        return
    
    try:

            return
        

            
            "full_name": callback.from_user.full_name or f"{callback.from_user.first_name} {callback.from_user.last_name or ''}".strip()
        }
        
        payment_response = await payment_gateway.create_payment(
                    user_id=callback.from_user.id,
                    vacancy_id=None,  
    payment_type = parts[4]  # 'individual' or 'legal_entity'
    

    await state.update_data(
        vacancy_id=vacancy_id,
        amount=amount,
        payment_type=payment_type
    )
    
    if payment_type == "individual":

        await handle_individual_payment(callback, state)
    elif payment_type == "legal_entity":

    
    from payment_handler import create_invoice
    from aiogram.types import LabeledPrice
    from config import get_settings
    
    settings = get_settings()
    

        )
        
        await callback.bot.send_invoice(
            chat_id=callback.from_user.id,
            **invoice_data
        )
        
        await callback.answer()
        await state.clear()
    except Exception as e:
        logger.error(f"Error creating invoice: {e}", exc_info=True)
        await callback.answer("❌ Ошибка при создании счета", show_alert=True)
        await state.clear()


@router.message(PaymentCompanyInfoStates.waiting_company_inn)
async def process_payment_company_inn(message: Message, state: FSMContext) -> None:
    """Обработка ИНН компании с автоматическим получением данных из DaData."""
    inn = message.text.strip()
    

        )
        return
    

        )
        return
    

    await state.update_data(
        company_inn=inn,
        company_name=company_data.get("name"),
        company_kpp=company_data.get("kpp"),
        company_address=company_data.get("address"),
        company_email=company_data.get("email"),  
        logger.error(f"Ошибка парсинга callback data '{callback.data}': {e}", exc_info=True)
        await callback.answer("❌ Ошибка: неверный формат данных", show_alert=True)
        return
    
    await state.update_data(
        tariff_id=tariff_id,
        input_method="file"
    )
    await state.set_state(PaymentCompanyInfoStates.waiting_company_file)
    
    await callback.message.answer(
        f"📄 <b>Отправьте файл с реквизитами компании</b>\n\n"
        f"{'─' * 30}\n\n"
        f"📦 Тариф: <b>{tariff.name}</b>\n"
        f"💰 Сумма: <b>{tariff.price:,} ₽</b>\n\n"
        f"{'─' * 30}\n\n"
        f"📋 <b>Поддерживаемые форматы:</b>\n"
        f"• PDF документы\n"
        f"• DOCX документы\n"
        f"• Изображения (JPG, PNG, BMP)\n\n"
        f"💡 <b>Файл должен содержать:</b>\n"
        f"• Название компании\n"
        f"• ИНН (10 цифр)\n"
        f"• КПП (9 цифр, опционально)\n"
        f"• Адрес (опционально)\n"
        f"• Email (опционально)\n\n"
        f"📤 Отправьте файл в этом сообщении"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("tariff_legal_input_manual_"))
async def handle_tariff_legal_input_manual(callback: CallbackQuery, state: FSMContext) -> None:
    """Обработка выбора ручного ввода для тарифа."""
    logger.info(f"handle_tariff_legal_input_manual вызван с callback.data: {callback.data}")
    

    


            return
        
        tariff_id = parts[4]  
        logger.error(f"Ошибка парсинга callback data '{callback.data}': {e}", exc_info=True)
        await callback.answer("❌ Ошибка: неверный формат данных", show_alert=True)
        return
    
    await state.update_data(
        tariff_id=tariff_id,
        input_method="manual"
    )

    import tempfile
    import os
    
    file_id = None
    filename = None
    

    if message.document:
        file_id = message.document.file_id
        filename = message.document.file_name or "file"
    elif message.photo:

        )
        return
    

    try:
        file = await message.bot.get_file(file_id)
        

        fd, temp_path = tempfile.mkstemp()
        os.close(fd)
        
        try:
            await message.bot.download_file(file.file_path, temp_path)
            

                )
                return
            

            company_info = extract_company_info_from_text(text)
            

                )
                return
            
            inn = company_info["inn"]
            

                )
                return
            

            await state.update_data(
                company_name=company_data.get("name"),
                company_inn=inn,
                company_kpp=company_data.get("kpp"),
                company_address=company_data.get("address"),
                company_email=company_data.get("email"),
                company_opf=company_data.get("opf")  
            "full_name": message.from_user.full_name or f"{message.from_user.first_name} {message.from_user.last_name or ''}".strip()
        }
        

        payment_response = await payment_gateway.create_payment(
            user_id=message.from_user.id,
            vacancy_id=None,  
                f"{'─' * 30}\n\n"
                f"📋 <b>Детали платежа:</b>\n"
                f"🆔 ID платежа: <b>{payment_id}</b>\n"
                f"📦 Тариф: <b>{tariff.name}</b>\n"
                f"💰 Сумма: <b>{tariff.price:,} ₽</b>\n\n"
                f"📋 <b>Что включено:</b>\n"
                f"• Вакансий: <b>{tariff.vacancies_count}</b>\n"
                f"• Анализов офферов: <b>{tariff.offer_analyses_count}</b>\n\n"
                f"{'─' * 30}\n\n"
                f"🏢 <b>Данные компании:</b>\n"
                f"Название: {company_name}\n"
                f"ИНН: {company_inn}\n"
                f"{f'КПП: {company_kpp}' if company_kpp else ''}\n"
                f"{f'Адрес: {company_address}' if company_address else ''}\n"
                f"{f'Email: {email}' if email else ''}\n\n"
                f"{'─' * 30}\n\n"
                f"💳 <b>Для оплаты перейдите по ссылке:</b>"
            )
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(text="💳 Оплатить", url=payment_url)
            ]])
            
            await message.answer(text, reply_markup=keyboard)
            
            await message.answer(
                f"💡 <b>После оплаты:</b>\n"
                f"• Чек самозанятого будет создан автоматически\n"
                f"• Вакансии и попытки анализа будут активированы\n"
                f"• Документы будут отправлены на указанный email (если указан)."
            )
            

            reply_markup=get_main_menu()
        )
        await state.clear()
        return
    
    try:

            f"user_id={message.from_user.id}, vacancy_id={vacancy_id}, "
            f"amount={total_price}, company_name={company_name}, inn={company_inn}"
        )
        

        telegram_data = {
            "username": message.from_user.username,
            "full_name": message.from_user.full_name or f"{message.from_user.first_name} {message.from_user.last_name or ''}".strip()
        }
        
        payment_response = await payment_gateway.create_payment(
            user_id=message.from_user.id,
            vacancy_id=vacancy_id,
            payment_type="legal_entity",
            amount=float(total_price),
            currency="RUB",
            company_info={
                "name": company_name,
                "inn": company_inn,
                "kpp": company_kpp,
                "legal_address": company_address,
                "email": email,
                "amount": amount  
        logger.info(f"Платеж создан успешно: payment_id={payment_response.get('payment_id')}")
        
        payment_id = payment_response.get("payment_id")
        payment_url = payment_response.get("payment_url")
        
        if payment_url:

            ]])
            
            await message.answer(text, reply_markup=keyboard)
            


    

    data = await state.get_data()
    

    

    parts = callback.data.split("_")
    if len(parts) >= 3 and parts[2] == "tariff":

            await state.clear()
    else:


    

    data = await state.get_data()
    

    


    payment_id = int(callback.data.split("_")[2])
    
    try:
        payment_gateway = get_payment_gateway_client()
        payment_status = await payment_gateway.get_payment_status(payment_id)
        

            return
        
        status = payment_status.get("status")
        

        if status == "completed":
            await handle_check_payment_status(callback)
            return
        


            return
        


        


    if callback.data.startswith("check_tariff_payment_"):
        payment_id = int(callback.data.split("_")[3])
    else:
        payment_id = int(callback.data.split("_")[2])
    
    try:
        payment_gateway = get_payment_gateway_client()
        payment_status = await payment_gateway.get_payment_status(payment_id)
        

            return
        
        status = payment_status.get("status")
        metadata = payment_status.get("metadata", {})
        is_test_mode = metadata.get("test_mode", False)
        payment_type = payment_status.get("payment_type")
        company_info = metadata.get("company_info", {})
        
        if status == "completed":

            if payment_type == "individual" and company_info.get("tariff_id"):
                tariff_id = company_info.get("tariff_id")
                tariff = get_tariff(tariff_id)
                
                if tariff:


            

            else:

                
        elif status == "pending":

            if payment_type == "individual":
                try:

                    settings = get_settings()
                    async with httpx.AsyncClient() as client:
                        sync_response = await client.post(
                            f"{settings.payment_gateway_url}/api/v1/payments/{payment_id}/sync-status",
                            timeout=10.0
                        )
                        if sync_response.status_code == 200:
                            sync_data = sync_response.json()
                            if sync_data.get("new_status") == "completed":


                                payment_status = await payment_gateway.get_payment_status(payment_id)
                                status = payment_status.get("status")

                                if status == "completed":

                                    if payment_type == "individual" and company_info.get("tariff_id"):
                                        tariff_id = company_info.get("tariff_id")
                                        tariff = get_tariff(tariff_id)
                                        
                                        if tariff:


