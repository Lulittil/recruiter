"""
Модуль для форматирования анализа видеоконференции.
"""
import re
from datetime import datetime
from typing import Optional


class AnalysisFormatter:
    """Класс для форматирования анализа видеоконференции."""
    
    @staticmethod
    def extract_recommendation(analysis_text: str) -> tuple[str, str]:
        """
        Извлечь рекомендацию из текста анализа.
        Returns: (recommendation_text, recommendation_hashtag)
        """
        if not analysis_text:
            return "", ""
        
        text_lower = analysis_text.lower()
        


            re.I | re.MULTILINE
        )
        match = recommendation_pattern.search(analysis_text)
        if match:
            recommendation_text = match.group(1).strip()
            recommendation_lower = recommendation_text.lower()
            

                return recommendation_text, "
            r'слаб[а-я]*\s*сторон[а-я]*.*?(?=\d+\.|###|$)',
            re.I | re.DOTALL
        )
        weaknesses_match = weaknesses_pattern.search(analysis_text)
        
        if strengths_match or weaknesses_match:
            sides = []
            if strengths_match:
                strengths_text = strengths_match.group(0)[:200]
                sides.append(f"✅ Сильные: {AnalysisFormatter._summarize_text(strengths_text)}")
            if weaknesses_match:
                weaknesses_text = weaknesses_match.group(0)[:200]
                sides.append(f"⚠️ Слабые: {AnalysisFormatter._summarize_text(weaknesses_text)}")
            if sides:
                sections.append(f"⚖️ <b>Оценка:</b> {' | '.join(sides)}")
        

            re.I | re.DOTALL
        )
        motivation_match = motivation_pattern.search(analysis_text)
        if motivation_match:
            motivation_text = motivation_match.group(0)[:200]
            sections.append(f"🎯 <b>Мотивация:</b> {AnalysisFormatter._summarize_text(motivation_text)}")
        

        if not sections:

            summary = analysis_text[:500].strip()

            if len(analysis_text) > 500:
                sections[0] += "..."
        
        return "\n\n".join(sections[:4])  
        text = re.sub(r'\s+', ' ', text).strip()
        
        if len(text) <= max_length:
            return text
        

        sentences = re.split(r'([.!?]\s+)', text)
        result = ""
        for i in range(0, len(sentences), 2):
            if i + 1 < len(sentences):
                candidate = result + sentences[i] + sentences[i + 1]
            else:
                candidate = result + sentences[i]
            
            if len(candidate) <= max_length:
                result = candidate
            else:
                break
        
        if result:
            return result.strip() + "..."
        else:

        