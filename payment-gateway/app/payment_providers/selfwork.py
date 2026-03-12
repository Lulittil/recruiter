"""
Интеграция с pro.selfwork.ru для оплаты от физических лиц.
"""
import logging
import hashlib
import re
from typing import Dict, Any, Optional
from decimal import Decimal
import httpx

from .base import PaymentProvider
from ..config import get_settings

logger = logging.getLogger(__name__)


class SelfworkProvider(PaymentProvider):
    """Провайдер платежей Selfwork (pro.selfwork.ru)."""
    
    def __init__(self):
        settings = get_settings()


        self.api_base_url = settings.selfwork_api_base_url or "https://pro.selfwork.ru/merchant/v1"
        self.webhook_secret = settings.selfwork_webhook_secret
        self.api_key = settings.selfwork_api_key

        """
        if not self.webhook_secret:
            logger.warning("Selfwork webhook secret not configured, signature may be invalid")
            return ""
        



        """
        if not self.webhook_secret:
            error_msg = (
                "Selfwork webhook secret is required for creating payments. "
                "Please set SELFWORK_WEBHOOK_SECRET environment variable. "
                "You can obtain it from your Selfwork account at pro.selfwork.ru"
            )
            logger.error(error_msg)
            raise ValueError(error_msg)
        

        amount_kopecks = int(amount * 100)
        order_id = str(payment_id)
        

        if len(order_id) > 35:
            logger.warning(f"order_id too long ({len(order_id)} chars), truncating to 35")
            order_id = order_id[:35]
        

        signature = self._generate_signature(order_id, amount_kopecks)
        

        








        form_data = {
            "order_id": order_id,
            "amount": str(amount_kopecks),
            "signature": signature,
            "info[0][name]": service_name,
            "info[0][quantity]": "1",
            "info[0][amount]": str(amount_kopecks),  
                        r'<meta[^>]*http-equiv=["\']refresh["\'][^>]*content=["\'][^"\']*url=([^"\';]+)',
                        r'<meta[^>]*http-equiv=["\']refresh["\'][^>]*url=["\']([^"\']+)["\']',
                        r'content=["\'][^"\']*url=([^"\';]+)',
                    ]
                    
                    for pattern in redirect_patterns:
                        redirect_match = re.search(pattern, html_content, re.IGNORECASE)
                        if redirect_match:
                            payment_url = redirect_match.group(1).strip()
                            break
                    

                    if not payment_url:
                        form_match = re.search(r'<form[^>]*action=["\']([^"\']+)["\']', html_content, re.IGNORECASE)
                        if form_match:
                            payment_url = form_match.group(1)
                    

                    if not payment_url:
                        link_patterns = [
                            r'<a[^>]*href=["\']([^"\']*payment[^"\']*)["\']',
                            r'<a[^>]*href=["\']([^"\']*pay[^"\']*)["\']',
                            r'<button[^>]*onclick=["\'][^"\']*location\.href=["\']([^"\']+)["\']',
                        ]
                        for pattern in link_patterns:
                            link_match = re.search(pattern, html_content, re.IGNORECASE)
                            if link_match:
                                payment_url = link_match.group(1)
                                break
                    

                    if payment_url and not payment_url.startswith(('http://', 'https://')):
                        if payment_url.startswith('/'):
                            payment_url = f"https://pro.selfwork.ru{payment_url}"
                        else:
                            payment_url = f"https://pro.selfwork.ru/{payment_url}"
                    



                    if not payment_url:


                        error_patterns = [

                            r'window\.smzInitError\s*=\s*\{[^}]*"errorMessage"\s*:\s*"([^"]+)"',
                            r'window\.smzInitError\s*=\s*\{[^}]*"errorMessage"\s*:\s*\'([^\']+)\'',

                            r'\{[^}]*"error"\s*:\s*true[^}]*"errorMessage"\s*:\s*"([^"]+)"',
                            r'\{[^}]*"error"\s*:\s*true[^}]*"errorMessage"\s*:\s*\'([^\']+)\'',

                            r'<[^>]*class=["\'][^"\']*error[^"\']*["\'][^>]*>([^<]+(?:<[^>]+>[^<]+)*)',
                            r'<[^>]*id=["\'][^"\']*error[^"\']*["\'][^>]*>([^<]+(?:<[^>]+>[^<]+)*)',

                            r'<[^>]*class=["\'][^"\']*alert[^"\']*["\'][^>]*>([^<]+(?:<[^>]+>[^<]+)*)',
                            r'<[^>]*class=["\'][^"\']*danger[^"\']*["\'][^>]*>([^<]+(?:<[^>]+>[^<]+)*)',


                        ]
                        
                        error_text = None
                        for pattern in error_patterns:
                            error_match = re.search(pattern, html_content, re.IGNORECASE | re.DOTALL)
                            if error_match:
                                error_text = error_match.group(1).strip()

                                try:
                                    error_text = error_text.encode().decode('unicode_escape')
                                except:
                                    pass

                                error_text = re.sub(r'<[^>]+>', ' ', error_text)
                                error_text = re.sub(r'\s+', ' ', error_text).strip()
                                if error_text and len(error_text) > 5:  
                        f"Try one of these alternatives: {', '.join(alternative_urls)}. "
                        f"Response: {error_text[:200]}"
                    )
                else:
                    error_text = response.text[:500] if response.text else "No response body"
                    logger.error(
                        f"Failed to create Selfwork payment: "
                        f"status={response.status_code}, response={error_text}"
                    )
                    raise ValueError(
                        f"Failed to create payment in Selfwork: "
                        f"HTTP {response.status_code}. Response: {error_text[:200]}"
                    )
                    
        except httpx.TimeoutException:
            logger.error(f"Timeout while creating Selfwork payment: payment_id={payment_id}")
            raise RuntimeError("Timeout while creating payment in Selfwork")
        except httpx.RequestError as e:
            logger.error(f"Request error while creating Selfwork payment: {e}")
            raise RuntimeError(f"Request error while creating payment: {str(e)}")
        except ValueError as e:

        """
        if not self.api_key:
            logger.warning("Selfwork API key not configured, cannot check payment status")
            return {"status": "unknown", "error": "API key not configured"}
        
        try:


            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://pro.selfwork.ru/merchant/v1/status",
                    params={"order_id": provider_payment_id},
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                        "Accept": "application/json"
                    },
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"Selfwork payment status retrieved: order_id={provider_payment_id}, status={data.get('status')}")
                    

        """
        if not self.webhook_secret:
            logger.warning("Selfwork webhook secret not configured")
            return False
        


        signature_string = f"{payment_id}:{amount}:{self.webhook_secret}"
        expected_signature = hashlib.sha256(signature_string.encode()).hexdigest()
        
        return signature.lower() == expected_signature.lower()

