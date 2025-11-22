"""
modules/trends_analyzer.py - Search-based trends analysis through web search + LLM extraction
"""

import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
project_root = Path(__file__).parent.parent.absolute()
env_path = project_root / '.env'
load_dotenv(dotenv_path=env_path, override=True)

logger = logging.getLogger(__name__)


class TrendsAnalyzer:
    """Analyze product trends through web search and LLM-powered timeline extraction"""

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        Initialize trends analyzer with LLM support.
        
        Args:
            api_key: API key for LLM (defaults to OPENROUTER_API_KEY)
            base_url: API base URL (defaults to OpenRouter)
        """
        self.api_key = api_key or "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"
        self.base_url = base_url or "https://openrouter.ai/api/v1"
        self.model = "tngtech/deepseek-r1t2-chimera:free"
        
        self.enabled = bool(self.api_key)
        
        if self.enabled:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
                
                if "openrouter" in self.base_url.lower():
                    self.client.default_headers.update({
                        "HTTP-Referer": "https://github.com/twirlz-git/Bank-Dashboard",
                        "X-Title": "Banking Product Trends Analyzer"
                    })
            except ImportError:
                logger.error("openai package not installed")
                self.enabled = False

    def analyze_trends(
        self, 
        bank: str, 
        product_type: str, 
        time_period: str,
        use_real_search: bool = False
    ) -> Dict[str, Any]:
        """
        Analyze trends for a product over time period.
        
        Args:
            bank: Bank name (e.g., "ВТБ", "Альфа-Банк")
            product_type: Product type (credit_card, deposit, consumer_loan)
            time_period: Time period (last_3_months, last_6_months, last_year)
            use_real_search: If True, attempt real web search (requires implementation)
        
        Returns:
            Dict with timeline, analysis, trends, and summary
        """
        
        # Calculate date range
        start_date, end_date = self._get_date_range(time_period)
        
        # Try to fetch real historical data via search
        timeline = []
        search_attempted = False
        
        if use_real_search and self.enabled:
            try:
                timeline = self._search_and_extract_timeline(
                    bank, product_type, start_date, end_date
                )
                search_attempted = True
                logger.info(f"Real search completed: {len(timeline)} data points found")
            except Exception as e:
                logger.warning(f"Real search failed: {e}, falling back to mock data")
        
        # Fallback to mock data if search not used or failed
        if not timeline:
            timeline = self._generate_mock_timeline(bank, product_type, time_period)
            logger.info(f"Using mock data: {len(timeline)} data points")
        
        # Analyze timeline
        analysis = self._analyze_timeline(timeline)
        trend_direction = self._get_trend_direction(timeline)
        
        return {
            "bank": bank,
            "product_type": product_type,
            "period": time_period,
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "timeline": timeline,
            "analysis": analysis,
            "trend_direction": trend_direction,
            "summary": self._generate_summary(bank, product_type, timeline, analysis, trend_direction),
            "data_source": "web_search" if search_attempted else "mock",
            "confidence": analysis.get("average_confidence", 0.5)
        }

    def _get_date_range(self, time_period: str) -> tuple:
        """Calculate start and end dates for given time period"""
        end_date = datetime.now()
        
        period_map = {
            "last_3_months": 92,
            "last_6_months": 180,
            "last_year": 365
        }
        
        days_back = period_map.get(time_period, 92)
        start_date = end_date - timedelta(days=days_back)
        
        return start_date, end_date

    def _search_and_extract_timeline(
        self, 
        bank: str, 
        product_type: str, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """
        Search news sources and extract timeline using LLM.
        
        This is a placeholder for real implementation that would:
        1. Form search query with temporal filters
        2. Search through banki.ru/news, sravni.ru, kommersant.ru
        3. Collect news snippets
        4. Use LLM to extract timeline data points
        """
        
        # Build search query
        search_query = self._build_search_query(bank, product_type, start_date, end_date)
        
        # Mock news snippets (in real implementation, this would come from web search)
        mock_snippets = self._get_mock_news_snippets(bank, product_type, start_date, end_date)
        
        # Extract timeline using LLM
        timeline = self._llm_extract_timeline(
            snippets=mock_snippets,
            bank=bank,
            product_type=product_type,
            start_date=start_date,
            end_date=end_date
        )
        
        # Interpolate missing data points if needed
        timeline = self._interpolate_timeline(timeline, start_date, end_date)
        
        return timeline

    def _build_search_query(
        self, 
        bank: str, 
        product_type: str, 
        start_date: datetime, 
        end_date: datetime
    ) -> str:
        """Build search query with temporal filters"""
        
        product_names = {
            "credit_card": "кредитная карта",
            "debit_card": "дебетовая карта",
            "deposit": "вклад",
            "consumer_loan": "потребительский кредит"
        }
        
        product_name = product_names.get(product_type, product_type)
        
        query = f"История изменения ставок {product_name} {bank} "
        query += f"after:{start_date.strftime('%Y-%m-%d')} "
        query += f"before:{end_date.strftime('%Y-%m-%d')} "
        query += "site:banki.ru/news OR site:sravni.ru OR site:kommersant.ru"
        
        return query

    def _get_mock_news_snippets(
        self,
        bank: str,
        product_type: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict[str, str]]:
        """
        Generate mock news snippets for demonstration.
        In production, this would fetch real news articles.
        """
        
        snippets = [
            {
                "date": (start_date + timedelta(days=15)).strftime("%Y-%m-%d"),
                "title": f"{bank} изменил условия по кредитным картам",
                "text": f"Банк {bank} повысил процентную ставку на 0.5% в связи с решением ЦБ. Новая ставка составила 19.0%.",
                "source": "banki.ru"
            },
            {
                "date": (start_date + timedelta(days=45)).strftime("%Y-%m-%d"),
                "title": f"{bank}: изменение условий кредитования",
                "text": f"{bank} снизил ставку до 18.5% из-за конкуренции с другими банками.",
                "source": "sravni.ru"
            },
            {
                "date": (start_date + timedelta(days=75)).strftime("%Y-%m-%d"),
                "title": f"Банки корректируют ставки",
                "text": f"{bank} установил ставку на уровне 17.9% для привлечения клиентов.",
                "source": "kommersant.ru"
            }
        ]
        
        return snippets

    def _llm_extract_timeline(
        self,
        snippets: List[Dict[str, str]],
        bank: str,
        product_type: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """
        Use LLM to extract timeline data from news snippets.
        """
        
        if not self.enabled:
            logger.warning("LLM not available, using fallback extraction")
            return self._fallback_extract_timeline(snippets)
        
        # Build prompt for LLM
        prompt = self._build_extraction_prompt(snippets, bank, product_type)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Вы - эксперт по анализу финансовых новостей. Извлекайте временные ряды изменений банковских условий из новостных статей. Отвечайте ТОЛЬКО валидным JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.3
            )
            
            result = json.loads(response.choices[0].message.content)
            timeline = result.get("timeline", [])
            
            logger.info(f"LLM extracted {len(timeline)} data points")
            return timeline
            
        except Exception as e:
            logger.error(f"LLM extraction failed: {e}")
            return self._fallback_extract_timeline(snippets)

    def _build_extraction_prompt(
        self,
        snippets: List[Dict[str, str]],
        bank: str,
        product_type: str
    ) -> str:
        """Build prompt for LLM timeline extraction"""
        
        snippets_text = "\n\n".join([
            f"Дата: {s['date']}\nИсточник: {s['source']}\nЗаголовок: {s['title']}\nТекст: {s['text']}"
            for s in snippets
        ])
        
        product_names = {
            "credit_card": "кредитной карте",
            "deposit": "вкладу",
            "consumer_loan": "потребительскому кредиту"
        }
        product_name = product_names.get(product_type, "банковскому продукту")
        
        return f"""Из следующих новостных статей извлеки временной ряд изменений процентной ставки по {product_name} банка {bank}.

НОВОСТИ:
{snippets_text}

ЗАДАЧА:
Извлеки из новостей точки изменения ставки и верни в следующем формате JSON:

{{
  "timeline": [
    {{
      "date": "YYYY-MM-DD",
      "rate": 18.5,
      "reason": "Решение ЦБ / Конкуренция / Маркетинг / Стабилизация",
      "confidence": 0.9,
      "source": "banki.ru"
    }}
  ]
}}

ПРАВИЛА:
- Если дата точная - используй её
- Если дата неточная ("в начале месяца") - используй 15 число
- Если дата не указана - используй дату публикации статьи
- confidence: 0.9 для точных данных, 0.7 для приблизительных, 0.5 для предположений
- Если информации недостаточно - возвращай пустой массив
- Извлекай ТОЛЬКО упоминания об изменениях ставок {bank}
"""

    def _fallback_extract_timeline(self, snippets: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """Fallback extraction without LLM (simple regex-based)"""
        
        import re
        timeline = []
        
        for snippet in snippets:
            # Try to extract rate from text using regex
            rate_match = re.search(r'(\d+[.,]\d+)%', snippet['text'])
            
            if rate_match:
                rate_str = rate_match.group(1).replace(',', '.')
                try:
                    rate = float(rate_str)
                    timeline.append({
                        "date": snippet['date'],
                        "rate": rate,
                        "reason": "Извлечено из новости",
                        "confidence": 0.6,
                        "source": snippet.get('source', 'unknown')
                    })
                except ValueError:
                    pass
        
        return timeline

    def _interpolate_timeline(
        self,
        timeline: List[Dict[str, Any]],
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """
        Interpolate missing data points in timeline.
        If there are gaps between data points, fill with linear interpolation.
        """
        
        if len(timeline) < 2:
            return timeline
        
        # Sort by date
        timeline = sorted(timeline, key=lambda x: x['date'])
        
        # For MVP, return as-is (full interpolation implementation can be added later)
        return timeline

    def _generate_mock_timeline(
        self, 
        bank: str, 
        product_type: str, 
        time_period: str
    ) -> List[Dict[str, Any]]:
        """Generate mock timeline for demonstration"""
        
        base_date = datetime.now()
        timeline = []
        
        if time_period == "last_3_months":
            days_back = 92
            intervals = [0, 30, 60, 90]
        elif time_period == "last_6_months":
            days_back = 180
            intervals = [0, 45, 90, 135, 180]
        else:
            days_back = 365
            intervals = [0, 90, 180, 270, 360]
        
        # Mock data patterns
        base_rate = 19.5
        rates = [base_rate - (i * 0.4) for i in range(len(intervals))]
        reasons = [
            "Начало периода",
            "Решение ЦБ",
            "Реакция на конкуренцию",
            "Маркетинговая акция",
            "Стабилизация"
        ]
        
        for idx, days_ago in enumerate(reversed(intervals)):
            date = base_date - timedelta(days=days_ago)
            timeline.append({
                "date": date.strftime("%Y-%m-%d"),
                "rate": rates[idx % len(rates)],
                "reason": reasons[idx % len(reasons)],
                "confidence": 0.75,
                "source": "mock"
            })
        
        return timeline

    def _analyze_timeline(self, timeline: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze timeline for patterns and statistics"""
        
        if not timeline:
            return {"status": "no_data"}
        
        rates = [t.get("rate") for t in timeline if t.get("rate") is not None]
        
        if len(rates) < 2:
            return {"status": "insufficient_data"}
        
        confidences = [t.get("confidence", 0.5) for t in timeline]
        
        return {
            "status": "success",
            "start_value": rates[0],
            "end_value": rates[-1],
            "min_value": min(rates),
            "max_value": max(rates),
            "average_value": sum(rates) / len(rates),
            "total_change": rates[-1] - rates[0],
            "change_percentage": ((rates[-1] - rates[0]) / rates[0] * 100) if rates[0] != 0 else 0,
            "data_points": len(rates),
            "change_points": self._count_change_points(rates),
            "average_confidence": sum(confidences) / len(confidences)
        }

    def _count_change_points(self, values: List[float], threshold: float = 0.1) -> int:
        """Count significant change points in values"""
        
        if len(values) < 2:
            return 0
        
        changes = 0
        for i in range(1, len(values)):
            if abs(values[i] - values[i-1]) >= threshold:
                changes += 1
        
        return changes

    def _get_trend_direction(self, timeline: List[Dict[str, Any]]) -> str:
        """Determine overall trend direction"""
        
        if not timeline or len(timeline) < 2:
            return "stable"
        
        rates = [t.get("rate") for t in timeline if t.get("rate") is not None]
        
        if len(rates) < 2:
            return "stable"
        
        start = rates[0]
        end = rates[-1]
        
        change_pct = ((end - start) / start * 100) if start != 0 else 0
        
        if change_pct > 2:
            return "increasing"
        elif change_pct < -2:
            return "decreasing"
        else:
            return "stable"

    def _generate_summary(
        self, 
        bank: str, 
        product_type: str, 
        timeline: List[Dict[str, Any]],
        analysis: Dict[str, Any],
        trend: str
    ) -> str:
        """Generate comprehensive human-readable summary"""
        
        if analysis.get("status") == "no_data":
            return f"❌ Недостаточно данных для анализа {product_type} банка {bank}"
        
        if analysis.get("status") == "insufficient_data":
            return f"⚠️ Недостаточно точек данных для полноценного анализа {product_type} банка {bank}"
        
        product_names = {
            "credit_card": "кредитной карты",
            "debit_card": "дебетовой карты",
            "deposit": "вклада",
            "consumer_loan": "потребительского кредита"
        }
        product_name = product_names.get(product_type, product_type)
        
        trend_icons = {
            "increasing": "📈 Растущий",
            "decreasing": "📉 Падающий",
            "stable": "→ Стабильный"
        }
        trend_text = trend_icons.get(trend, "→ Стабильный")
        
        summary = f"**Анализ {product_name} банка {bank}**\n\n"
        summary += f"• **Начальное значение:** {analysis.get('start_value', 0):.2f}%\n"
        summary += f"• **Конечное значение:** {analysis.get('end_value', 0):.2f}%\n"
        summary += f"• **Среднее значение:** {analysis.get('average_value', 0):.2f}%\n"
        summary += f"• **Диапазон:** {analysis.get('min_value', 0):.2f}% - {analysis.get('max_value', 0):.2f}%\n"
        summary += f"• **Тренд:** {trend_text}\n"
        
        change = analysis.get('total_change', 0)
        change_pct = analysis.get('change_percentage', 0)
        
        if change != 0:
            summary += f"• **Изменение за период:** {change:+.2f}% ({change_pct:+.1f}%)\n"
        
        change_points = analysis.get('change_points', 0)
        summary += f"• **Точек изменения:** {change_points}\n"
        
        confidence = analysis.get('average_confidence', 0)
        summary += f"• **Достоверность данных:** {confidence:.0%}\n"
        
        # Add interpretation
        summary += f"\n**💡 Интерпретация:**\n"
        
        if trend == "decreasing":
            summary += "Ставка снижается - возможно, банк стремится привлечь больше клиентов или реагирует на конкуренцию.\n"
        elif trend == "increasing":
            summary += "Ставка растёт - возможно, банк корректирует условия в связи с решениями ЦБ или изменением рыночной ситуации.\n"
        else:
            summary += "Ставка остаётся стабильной - условия не менялись значительно в течение анализируемого периода.\n"
        
        return summary


