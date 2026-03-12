"""
Сервис для отправки уведомлений пользователям через Telegram.
"""
import logging
from typing import Optional
import httpx

from ..config import get_settings

logger = logging.getLogger(__name__)


class TelegramNotifier:
    """Сервис для отправки уведомлений через Telegram."""
    
    def __init__(self):
        self.settings = get_settings()


        """

        if self.core_bot_webhook_url:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{self.core_bot_webhook_url}/notify/payment-success",
                        json={
                            "user_id": user_id,
                            "tariff_name": tariff_name,
                            "payment_id": payment_id
                        },
                        timeout=10.0
                    )
                    if response.status_code == 200:
                        logger.info(f"Notification sent to user {user_id} about payment {payment_id}")
                        return True
            except Exception as e:
                logger.warning(f"Failed to send notification via webhook: {e}")
        

        logger.info(
            f"Payment success notification for user {user_id}, "
            f"tariff {tariff_name}, payment_id {payment_id}"
        )
        return False

