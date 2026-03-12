"""
Обработчик платежей через Telegram Payments.
"""
import logging
from typing import Dict, Any, Optional
from aiogram import Router, F
from aiogram.types import Message, PreCheckoutQuery, SuccessfulPayment, LabeledPrice

from db_client import DBClient, get_db_client
from config import get_settings

logger = logging.getLogger(__name__)

router = Router()


async def create_invoice(
    title: str,
    description: str,
    payload: str,
    prices: list[LabeledPrice],
    provider_token: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create invoice for payment.
    
    Args:
        title: Invoice title
        description: Invoice description
        payload: Unique payload for this invoice
        prices: List of prices
        provider_token: Payment provider token
        
    Returns:
        Invoice data for send_invoice
    """
    settings = get_settings()
    
    
                                f"Ссылка: {receipt_response.get('receipt_url')}"
                            )
                except Exception as e:
                    logger.warning(f"Failed to create receipt via Payment Gateway: {e}")

    
    elif payload.startswith("tariff_"):
        