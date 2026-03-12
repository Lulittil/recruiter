"""
Клиент для работы с DeepSeek API для анализа диалогов.
"""
import logging
from typing import Optional, Dict, Any
from openai import AsyncOpenAI
import os

logger = logging.getLogger(__name__)


class DeepSeekClient:
    """Клиент для DeepSeek API."""
    
    def __init__(self, api_key: Optional[str] = None, vacancy_id: Optional[int] = None):
        self._api_key = api_key or os.getenv("DEEPSEEK_API_KEY", "")
        self._vacancy_id = vacancy_id
        self._client: Optional[AsyncOpenAI] = None
    
    async def _ensure_client(self):
        """Инициализировать клиент DeepSeek."""
        if self._client is not None:
            return
        
        if not self._api_key:
            raise ValueError("DeepSeek API key is not set")
        


        try:
            response = await self._client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=3000
            )
            
            analysis = response.choices[0].message.content if response.choices else ""
            logger.info(f"Dialogue analysis completed, length: {len(analysis)} chars")
            return analysis
        except Exception as e:
            logger.error(f"Error analyzing dialogue: {e}", exc_info=True)
            raise

