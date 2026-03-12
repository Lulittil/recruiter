"""
Сервис для отправки уведомлений о чеках клиентам.
"""
import logging
from typing import Optional
import httpx

logger = logging.getLogger(__name__)


class WebhookNotifier:
    """Сервис для отправки уведомлений через webhook."""
    
    def __init__(self, webhook_url: Optional[str] = None):
        self.webhook_url = webhook_url
    
    async def send_receipt_notification(
        self,
        receipt_data: dict,
        telegram_chat_id: Optional[int] = None,
        email: Optional[str] = None
    ) -> bool:
        """
        Отправить уведомление о создании чека.
        
        Может отправлять через:
        - Telegram (если указан chat_id)
        - Email (если указан email)
        - Webhook (если настроен)
        """
        if not any([telegram_chat_id, email, self.webhook_url]):
            logger.warning("No notification channels configured")
            return False
        
        notification_data = {
            "receipt_number": receipt_data.get("receipt_number"),
            "receipt_url": receipt_data.get("receipt_url"),
            "qr_code_url": receipt_data.get("qr_code_url"),
            "amount": receipt_data.get("amount"),
            "tax_amount": receipt_data.get("tax_amount"),
            "client_name": receipt_data.get("client_name"),
        }
        

        if self.webhook_url:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        self.webhook_url,
                        json={
                            "type": "receipt_created",
                            "data": notification_data,
                            "telegram_chat_id": telegram_chat_id,
                            "email": email
                        },
                        timeout=10.0
                    )
                    response.raise_for_status()
                    logger.info(f"Receipt notification sent via webhook: {receipt_data.get('receipt_number')}")
                    return True
            except Exception as e:
                logger.error(f"Failed to send webhook notification: {e}")
        
        return False

