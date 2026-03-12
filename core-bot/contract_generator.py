"""
Модуль для генерации договора на оказание услуг в PDF.
"""
import os
import tempfile
import logging
import xml.sax.saxutils as saxutils
from datetime import datetime
from typing import Dict, Optional
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

logger = logging.getLogger(__name__)


def escape_text(text: str) -> str:
    """Экранирование специальных символов XML для корректного отображения в PDF."""
    return saxutils.escape(text)


def generate_service_contract(
    company_name: str,
    company_inn: str,
    company_kpp: Optional[str],
    company_address: Optional[str],
    service_description: str,
    amount: float,
    currency: str = "RUB",
    company_opf: Optional[Dict[str, Optional[str]]] = None
) -> str:
    """
    Генерация договора на оказание услуг в PDF.
    
    Args:
        company_name: Название компании-заказчика
        company_inn: ИНН компании
        company_kpp: КПП компании (опционально)
        company_address: Адрес компании (опционально)
        service_description: Описание услуги
        amount: Сумма договора
        currency: Валюта (по умолчанию RUB)
        
    Returns:
        Путь к созданному PDF файлу
    """

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    temp_path = temp_file.name
    temp_file.close()
    
    try:

        font_name = "Helvetica"
        bold_font_name = "Helvetica-Bold"
        font_registered = False
        

        font_paths = [

            ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "DejaVuSans", "DejaVuSans-Bold"),
            ("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", "LiberationSans", "LiberationSans-Bold"),

            ("/usr/share/fonts/TTF/DejaVuSans.ttf", "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf", "DejaVuSans", "DejaVuSans-Bold"),
            # Windows fonts (local development)
            ("C:/Windows/Fonts/arial.ttf", "C:/Windows/Fonts/arialbd.ttf", "ArialCyr", "ArialCyr-Bold"),
            ("C:/Windows/Fonts/ARIAL.TTF", "C:/Windows/Fonts/ARIALBD.TTF", "ArialCyr", "ArialCyr-Bold"),
            ("C:/Windows/Fonts/times.ttf", "C:/Windows/Fonts/timesbd.ttf", "TimesCyr", "TimesCyr-Bold"),
        ]
        
        for regular_path, bold_path, reg_name, bold_name in font_paths:
            try:
                if os.path.exists(regular_path):
                    pdfmetrics.registerFont(TTFont(reg_name, regular_path))
                    font_name = reg_name
                    font_registered = True
                    



        

        doc = SimpleDocTemplate(temp_path, pagesize=A4)
        story = []
        

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontName=bold_font_name,
            fontSize=16,
            textColor=colors.HexColor('#000000'),
            spaceAfter=30,
            alignment=1  # Center
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontName=bold_font_name,
            fontSize=12,
            textColor=colors.HexColor('#000000'),
            spaceAfter=12,
            spaceBefore=12
        )
        
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontName=font_name,
            fontSize=10,
            textColor=colors.HexColor('#000000'),
            spaceAfter=6,
            leading=14
        )
        

        story.append(Spacer(1, 0.5*cm))
        

        story.append(Spacer(1, 0.3*cm))
        

        )
        story.append(Paragraph(escape_text(executor_info), normal_style))
        story.append(Spacer(1, 0.2*cm))
        



        customer_info += "."
        
        story.append(Paragraph(escape_text(customer_info), normal_style))
        story.append(Spacer(1, 0.3*cm))
        

        story.append(Paragraph(escape_text(service_text), normal_style))
        story.append(Spacer(1, 0.3*cm))
        

        )
        story.append(Paragraph(escape_text(payment_text), normal_style))
        story.append(Spacer(1, 0.3*cm))
        

        )
        story.append(Paragraph(escape_text(terms_text), normal_style))
        story.append(Spacer(1, 0.3*cm))
        

        )
        story.append(Paragraph(escape_text(customer_obligations), normal_style))
        story.append(Spacer(1, 0.3*cm))
        

        )
        story.append(Paragraph(escape_text(responsibility_text), normal_style))
        story.append(Spacer(1, 0.3*cm))
        

        )
        story.append(Paragraph(escape_text(disputes_text), normal_style))
        story.append(Spacer(1, 0.3*cm))
        

        )
        story.append(Paragraph(escape_text(other_conditions), normal_style))
        story.append(Spacer(1, 0.5*cm))
        

        )
        story.append(Paragraph(customer_signature, normal_style))
        


        try:
            if os.path.exists(temp_path):
                os.remove(temp_path)
        except:
            pass
        raise

