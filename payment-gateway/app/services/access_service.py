"""
Сервис для предоставления доступа к услугам после оплаты.
"""
import logging
from typing import Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import httpx

from ..models import Payment, PaymentRecord, ActiveUser
from ..config import get_settings

logger = logging.getLogger(__name__)


class AccessService:
    """Сервис для управления доступом к услугам."""
    
    def __init__(self):
        self.settings = get_settings()
        self.db_core_url = self.settings.db_core_url
    
    async def grant_access_after_payment(
        self,
        session: AsyncSession,
        payment: Payment,
        auto_commit: bool = True
    ) -> bool:
        """
        Предоставить доступ к услуге после успешной оплаты.
        Создает запись об оплате и пользователя (если его еще нет).
        
        Args:
            session: Сессия БД
            payment: Объект платежа
            auto_commit: Автоматически делать commit (по умолчанию True)
            
        Returns:
            bool: Успешно ли предоставлен доступ
        """
        try:

            user_id = payment.user_id
            metadata = payment.payment_metadata or {}
            company_info = metadata.get("company_info", {})
            tariff_id = company_info.get("tariff_id")
            
            if not tariff_id:
                logger.warning(f"Tariff ID not found in payment: payment_id={payment.payment_id}")
                return False
            

            tariff_info = self._get_tariff_info(tariff_id)
            
            if not tariff_info:
                logger.warning(f"Unknown tariff: tariff_id={tariff_id}")
                return False
            

            await self._create_payment_record(session, payment, company_info, tariff_id, tariff_info)
            

            active_user = await self._create_or_update_active_user(
                session, payment, company_info, tariff_id, tariff_info
            )
            

            if auto_commit:
                await session.commit()
            else:
                await session.flush()
            
            logger.info(
                f"Access granted: user_id={user_id}, "
                f"tariff_id={tariff_id}, payment_id={payment.payment_id}"
            )
            

            try:
                from .telegram_notifier import TelegramNotifier
                notifier = TelegramNotifier()
                await notifier.notify_payment_success(
                    user_id=user_id,
                    tariff_name=tariff_info["name"],
                    payment_id=payment.payment_id
                )
            except Exception as e:
                logger.warning(f"Failed to notify user about access: {e}")


        stmt = select(PaymentRecord).where(PaymentRecord.payment_id == payment.payment_id)
        result = await session.execute(stmt)
        existing_record = result.scalar_one_or_none()
        
        if existing_record:
            logger.info(f"Payment record already exists: payment_id={payment.payment_id}")
            return existing_record
        

        payer_type = payment.payment_type  # 'individual' или 'legal_entity'
        

        company_name = company_info.get("name") or company_info.get("company_name")
        company_inn = company_info.get("inn") or company_info.get("company_inn")
        company_kpp = company_info.get("kpp") or company_info.get("company_kpp")
        company_ogrn = company_info.get("ogrn") or company_info.get("company_ogrn")
        company_opf = company_info.get("opf") or company_info.get("company_opf")
        company_address = company_info.get("legal_address") or company_info.get("address")
        company_email = company_info.get("email") or company_info.get("company_email")
        

        individual_full_name = company_info.get("full_name") or company_info.get("individual_full_name")
        individual_inn = company_info.get("individual_inn")
        

        metadata = payment.payment_metadata or {}
        telegram_data = metadata.get("telegram_data", {})
        telegram_username = telegram_data.get("username")
        telegram_full_name = telegram_data.get("full_name")
        

        user_id = payment.user_id
        

        stmt = select(ActiveUser).where(ActiveUser.telegram_user_id == user_id)
        result = await session.execute(stmt)
        active_user = result.scalar_one_or_none()
        

        payer_type = payment.payment_type
        metadata = payment.payment_metadata or {}
        telegram_data = metadata.get("telegram_data", {})
        
        company_name = company_info.get("name") or company_info.get("company_name")
        company_inn = company_info.get("inn") or company_info.get("company_inn")
        company_kpp = company_info.get("kpp") or company_info.get("company_kpp")
        company_ogrn = company_info.get("ogrn") or company_info.get("company_ogrn")
        company_opf = company_info.get("opf") or company_info.get("company_opf")
        company_address = company_info.get("legal_address") or company_info.get("address")
        company_email = company_info.get("email") or company_info.get("company_email")
        
        individual_full_name = company_info.get("full_name") or company_info.get("individual_full_name")
        individual_inn = company_info.get("individual_inn")
        
        telegram_username = telegram_data.get("username")
        telegram_full_name = telegram_data.get("full_name")
        telegram_link = f"https://t.me/{telegram_username}" if telegram_username else None
        
        if active_user:

            active_user.user_type = payer_type
            active_user.telegram_username = telegram_username or active_user.telegram_username
            active_user.telegram_full_name = telegram_full_name or active_user.telegram_full_name
            active_user.telegram_link = telegram_link or active_user.telegram_link
            

            if payer_type == "legal_entity":
                active_user.company_name = company_name or active_user.company_name
                active_user.company_inn = company_inn or active_user.company_inn
                active_user.company_kpp = company_kpp or active_user.company_kpp
                active_user.company_ogrn = company_ogrn or active_user.company_ogrn
                active_user.company_opf = company_opf or active_user.company_opf
                active_user.company_address = company_address or active_user.company_address
                active_user.company_email = company_email or active_user.company_email
            else:
                active_user.individual_full_name = individual_full_name or active_user.individual_full_name
                active_user.individual_inn = individual_inn or active_user.individual_inn
            

            active_user.current_tariff_id = tariff_id
            active_user.current_tariff_name = tariff_info.get("name")
            active_user.tariff_purchased_at = datetime.utcnow()
            active_user.tariff_vacancies_count = tariff_info.get("vacancies_count")
            active_user.tariff_offer_analyses_count = tariff_info.get("offer_analyses_count")
            active_user.last_payment_date = datetime.utcnow()
            active_user.is_active = True
            
            logger.info(f"Active user updated: user_id={active_user.user_id}, telegram_user_id={user_id}")
        else:

                "vacancies_count": 10,
                "offer_analyses_count": 25
            }
        }
        return tariffs.get(tariff_id)

