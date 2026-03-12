"""
Модуль для сохранения транскрипций в файлы.
"""
import os
import logging
from datetime import datetime
from typing import List, Dict
import aiofiles

logger = logging.getLogger(__name__)


async def save_transcript_to_file(room_id: str, transcript: List[Dict], transcripts_dir: str):
    """
    Сохранить транскрипцию в текстовый файл.
    
    Формат файла:
    ========================================
    Транскрипция видеоконференции
    Комната: {room_id}
    Дата создания: {timestamp}
    ========================================
    
    [Timestamp] Тип: Текст
    ...
    """
    try:

        os.makedirs(transcripts_dir, exist_ok=True)
        

        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"room_{room_id}_{timestamp}.txt"
        filepath = os.path.join(transcripts_dir, filename)
        

            

            elif entry_type == "transcript":
                content_lines.append(f"[{time_str}] {name}: {text}")
            elif entry_type == "participant_joined":
                content_lines.append(f"[{time_str}] --- {text} ---")
            elif entry_type == "participant_left":
                content_lines.append(f"[{time_str}] --- {text} ---")
            else:
                content_lines.append(f"[{time_str}] {text}")
        
        content = "\n".join(content_lines)
        

        async with aiofiles.open(filepath, 'w', encoding='utf-8') as f:
            await f.write(content)
        
        logger.info(f"Transcript saved to {filepath}")
        return filepath
    
    except Exception as e:
        logger.error(f"Error saving transcript: {e}", exc_info=True)
        raise

