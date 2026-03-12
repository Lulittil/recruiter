"""
Модуль для работы с тарифами системы.
"""
from typing import Dict, Any
from dataclasses import dataclass


@dataclass
class Tariff:
    """Класс для описания тарифа."""
    id: str
    name: str
    vacancies_count: int
    offer_analyses_count: int
    price: int  