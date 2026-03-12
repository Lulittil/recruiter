"""
Модуль для парсинга реквизитов компании из файлов и текста.
"""
import re
import logging
import os
import tempfile
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)


def extract_text_from_file(file_path: str, filename: str) -> Tuple[str, Optional[str]]:
    """
    Извлечение текста из файла (PDF, DOCX, изображения).
    
    Args:
        file_path: Путь к файлу
        filename: Имя файла
        
    Returns:
        Tuple[текст, ошибка]
    """
    name = filename.lower()
    
    try:

        

        

        

    """
    result = {
        "name": None,
        "inn": None,
        "kpp": None,
        "address": None,
        "email": None
    }
    

    text = text.replace("\n", " ").replace("\r", " ")
    text = re.sub(r"\s+", " ", text)
    

    inn_match = re.search(inn_pattern, text, re.IGNORECASE)
    if inn_match:
        inn = inn_match.group(1)

        if len(inn) == 10:
            result["inn"] = inn
        elif len(inn) == 12:

            result["inn"] = inn[:10]
    

    kpp_match = re.search(kpp_pattern, text, re.IGNORECASE)
    if kpp_match:
        result["kpp"] = kpp_match.group(1)
    

    ]
    for pattern in name_patterns:
        name_match = re.search(pattern, text, re.IGNORECASE)
        if name_match:
            name = name_match.group(0).strip()

            name = re.sub(r"[\"»«]", "", name)
            if len(name) > 3 and len(name) < 200:
                result["name"] = name
                break
    

    ]
    for pattern in address_patterns:
        address_match = re.search(pattern, text, re.IGNORECASE)
        if address_match:
            address = address_match.group(1).strip()
            if len(address) > 10 and len(address) < 500:
                result["address"] = address
                break
    

                
                company_data = suggestions[0].get("data", {})
                

                

                name_data = company_data.get("name", {})
                company_name = name_data.get("full_with_opf") or name_data.get("short_with_opf") or name_data.get("full") or name_data.get("short")
                
                kpp = company_data.get("kpp")
                
                address_data = company_data.get("address", {})
                address = address_data.get("unrestricted_value") or address_data.get("value")
                

                emails = company_data.get("emails")
                email = None
                if emails and isinstance(emails, list) and len(emails) > 0:
                    email = emails[0] if isinstance(emails[0], str) else emails[0].get("value") if isinstance(emails[0], dict) else None
                

                opf_data = company_data.get("opf", {})
                opf_full = opf_data.get("full")  