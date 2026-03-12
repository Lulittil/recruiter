"""
Управление комнатами для видеоконференций.
"""
import secrets
import logging
from typing import Dict, Optional, Set
from datetime import datetime

logger = logging.getLogger(__name__)


class RoomManager:
    """Управляет комнатами видеоконференций."""
    
    def __init__(self):
        self._rooms: Dict[str, Dict] = {}  