"""
FastAPI приложение для видеоконференций с записью транскрипций.
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from typing import Dict, List, Optional, Any
import json
import logging
import asyncio
import os
import uuid

from .config import settings
from .room_manager import room_manager
from .transcript_recorder import save_transcript_to_file
from .db_client import get_db_client
from .deepseek_client import DeepSeekClient
from .kafka_producer import get_kafka_producer
from .analysis_formatter import AnalysisFormatter

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Video Conference Service")


                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    time_str = dt.strftime("%H:%M:%S")
                except:
                    time_str = timestamp
                
                dialogue_lines.append(f"[{time_str}] {name}: {text}")
        
        dialogue_text = "\n".join(dialogue_lines)
        if not dialogue_text.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Dialogue is empty"
            )
        

        vacancy_id = manager.get("vacancy_id")
        vacancy_name = None
        if vacancy_id:
            vacancy = await db_client.get_vacancy(vacancy_id)
            if vacancy:
                vacancy_name = vacancy.get("name", "")
        

        deepseek_token = None
        if vacancy_id:
            deepseek_token = await db_client.get_deepseek_token(vacancy_id)
        

        if not deepseek_token:
            deepseek_token = settings.DEEPSEEK_API_KEY
        
        if not deepseek_token:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="DeepSeek API key not configured"
            )
        

        deepseek_client = DeepSeekClient(api_key=deepseek_token)
        analysis = await deepseek_client.analyze_dialogue(dialogue_text, vacancy_name)
        

        formatted_analysis = AnalysisFormatter.format_analysis(
            analysis_text=analysis,
            room_id=room_id,
            vacancy_name=vacancy_name
        )
        

        manager_chat_id = manager.get("manager_chat_id")
        if not manager_chat_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Manager chat_id not found"
            )
        
        kafka_producer = await get_kafka_producer()
        
        response = {
            "response_id": str(uuid.uuid4()),
            "response_type": "text_message",
            "company_id": vacancy_id or 0,  