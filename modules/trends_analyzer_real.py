"""
modules/trends_analyzer_real.py - Real trends analysis using web search and LLM extraction
"""

import asyncio
import logging
import os
import json
import re
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import aiohttp

try:
    from configs.data_sources import DATA_SOURCES, SEARCH_PATTERNS, TIME_FILTERS
except:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from configs.data_sources import DATA_SOURCES, SEARCH_PATTERNS, TIME_FILTERS

logger = logging.getLogger(__name__)


class RealTrendsAnalyzer:
    """Real trends analysis using web search and LLM extraction"""
    
    def __init__(self):
        self.perplexity_api_key = os.getenv("PERPLEXITY_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
    
    async def analyze_trends(self, bank: str, product_type: str, period: str) -> Dict[str, Any]:
        """
        Main entry point for trends analysis
        
        Strategy:
        1. Search for news/changes via Perplexity API
        2. Extract timeline via LLM
        3. Fallback to mock if search fails
        """
        
        logger.info(f"Analyzing trends: {bank} {product_type} {period}")
        
        # Try real search first
        if self.perplexity_api_key:
            try:
                timeline = await self._search_and_extract_timeline(bank, product_type, period)
                
                if timeline and len(timeline) > 0:
                    analysis = self._analyze_timeline(timeline)
                    summary = self._generate_summary(timeline, analysis, bank, product_type)
                    
                    return {
                        "timeline": timeline,
                        "analysis": analysis,
                        "summary": summary,
                        "data_source": "real_search",
                        "bank": bank,
                        "product_type": product_type,
                        "period": period
                    }
            except Exception as e:
                logger.error(f"Real search failed: {e}")
        
        # Fallback to mock data
        logger.warning("Using mock data for trends")
        return await self._get_mock_trends(bank, product_type, period)
    
    async def _search_and_extract_timeline(self, bank: str, product_type: str, period: str) -> List[Dict[str, Any]]:
        """Search web and extract timeline using LLM"""
        
        # Step 1: Search for news
        search_results = await self._perplexity_search(bank, product_type, period)
        
        if not search_results:
            logger.warning("No search results")
            return []
        
        # Step 2: Extract timeline via LLM
        timeline = await self._extract_timeline_from_search(search_results, bank, product_type)
        
        return timeline
    
    async def _perplexity_search(self, bank: str, product_type: str, period: str) -> Optional[Dict[str, Any]]:
        """Search for historical changes via Perplexity API"""
        
        query = self._build_search_query(bank, product_type, period)
        
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {self.perplexity_api_key}",
                "Content-Type": "application/json"
            }
            
            # Map period to recency filter
            recency_map = {
                "last_3_months": "month",
                "last_6_months": "month",
                "last_year": "year"
            }
            
            payload = {
                "model": "sonar",
                "messages": [
                    {
                        "role": "system",
                        "content": "Ты эксперт по банковским продуктам. Найди все изменения условий с точными датами."
                    },
                    {
                        "role": "user",
                        "content": query
                    }
                ],
                "search_recency_filter": recency_map.get(period, "month"),
                "return_citations": True,
                "temperature": 0.1
            }
            
            try:
                async with session.post(
                    "https://api.perplexity.ai/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as resp:
                    if resp.status != 200:
                        logger.error(f"Perplexity error: {resp.status}")
                        text = await resp.text()
                        logger.error(f"Response: {text}")
                        return None
                    
                    result = await resp.json()
                    
                    return {
                        "content": result['choices'][0]['message']['content'],
                        "citations": result.get('citations', [])
                    }
                    
            except Exception as e:
                logger.error(f"Perplexity API failed: {e}")
                return None
    
    async def _extract_timeline_from_search(self, search_results: Dict[str, Any], 
                                           bank: str, product_type: str) -> List[Dict[str, Any]]:
        """Extract structured timeline from search results using OpenAI"""
        
        if not self.openai_api_key:
            logger.warning("No OpenAI key for extraction")
            return []
        
        content = search_results.get('content', '')
        citations = search_results.get('citations', [])
        
        extraction_prompt = f"""
Из следующего текста извлеки все изменения условий банковских продуктов {bank}:

{content}

Верни JSON-массив с изменениями в формате:
[
  {{
    "date": "YYYY-MM-DD",
    "rate": <число>,
    "reason": "краткое описание изменения",
    "source": "источник"
  }}
]

Правила:
- Если точная дата неизвестна ("в начале октября"), используй середину месяца
- Если указан только месяц, используй 15-е число
- Если информации нет, верни пустой массив []
- Включай только реальные изменения с указанными датами
"""
        
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {self.openai_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": "Ты эксперт по извлечению структурированных данных."},
                    {"role": "user", "content": extraction_prompt}
                ],
                "temperature": 0.1,
                "response_format": {"type": "json_object"}
            }
            
            try:
                async with session.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as resp:
                    if resp.status != 200:
                        logger.error(f"OpenAI error: {resp.status}")
                        return []
                    
                    result = await resp.json()
                    content = result['choices'][0]['message']['content']
                    
                    # Parse JSON
                    try:
                        data = json.loads(content)
                        # Handle both array and object with array
                        if isinstance(data, list):
                            timeline = data
                        elif isinstance(data, dict) and 'timeline' in data:
                            timeline = data['timeline']
                        elif isinstance(data, dict) and 'changes' in data:
                            timeline = data['changes']
                        else:
                            timeline = []
                        
                        # Sort by date
                        timeline.sort(key=lambda x: x.get('date', '2024-01-01'))
                        
                        return timeline
                        
                    except json.JSONDecodeError as e:
                        logger.error(f"JSON parse error: {e}")
                        return []
                    
            except Exception as e:
                logger.error(f"Timeline extraction failed: {e}")
                return []
    
    def _build_search_query(self, bank: str, product_type: str, period: str) -> str:
        """Build search query for news"""
        
        product_names = {
            "credit_card": "кредитная карта",
            "deposit": "вклад",
            "consumer_loan": "потребительский кредит"
        }
        
        product_ru = product_names.get(product_type, product_type)
        
        period_texts = {
            "last_3_months": "за последние 3 месяца",
            "last_6_months": "за последние 6 месяцев",
            "last_year": "за последний год"
        }
        
        period_text = period_texts.get(period, period)
        
        query = f"""
Найди все изменения условий по {product_ru} банка {bank} {period_text}.

Интересуют:
- Изменения процентных ставок
- Изменения кэшбэка
- Изменения комиссий и тарифов
- Новые условия и акции

Ищи в источниках: banki.ru, sravni.ru, kommersant.ru, rbc.ru, interfax.ru

Укажи для каждого изменения:
- Точную дату (или период)
- Старое и новое значение
- Причину изменения
"""
        
        return query
    
    def _analyze_timeline(self, timeline: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze timeline data"""
        
        if not timeline or len(timeline) == 0:
            return {"status": "no_data"}
        
        rates = [item.get('rate', 0) for item in timeline]
        
        if not rates:
            return {"status": "no_data"}
        
        analysis = {
            "status": "success",
            "start_value": rates[0],
            "end_value": rates[-1],
            "total_change": rates[-1] - rates[0],
            "average_value": sum(rates) / len(rates),
            "change_points": len(timeline) - 1,
            "min_value": min(rates),
            "max_value": max(rates)
        }
        
        return analysis
    
    def _generate_summary(self, timeline: List[Dict[str, Any]], analysis: Dict[str, Any],
                         bank: str, product_type: str) -> str:
        """Generate human-readable summary"""
        
        if analysis.get("status") != "success":
            return f"Данных об изменениях {product_type} {bank} не найдено."
        
        total_change = analysis['total_change']
        change_direction = "увеличилась" if total_change > 0 else "снизилась"
        
        summary = f"""
Ставка {change_direction} на {abs(total_change):.2f}% за период.
Начальное значение: {analysis['start_value']:.2f}%
Текущее значение: {analysis['end_value']:.2f}%
Зафиксировано изменений: {analysis['change_points']}
        """.strip()
        
        return summary
    
    async def _get_mock_trends(self, bank: str, product_type: str, period: str) -> Dict[str, Any]:
        """Generate mock trends data as fallback"""
        
        # Generate synthetic timeline
        now = datetime.now()
        
        period_days = {
            "last_3_months": 90,
            "last_6_months": 180,
            "last_year": 365
        }
        
        days = period_days.get(period, 90)
        num_points = min(5, days // 30)
        
        timeline = []
        base_rate = 25.0
        
        for i in range(num_points):
            date = now - timedelta(days=days - (i * days // num_points))
            rate = base_rate + (i * 0.5)  # Gradual increase
            
            timeline.append({
                "date": date.strftime("%Y-%m-%d"),
                "rate": round(rate, 2),
                "reason": f"Плановое изменение тарифов ({i+1}/{num_points})",
                "source": "mock_data"
            })
        
        analysis = self._analyze_timeline(timeline)
        summary = f"⚠️ Используются тестовые данные. Реальные изменения не найдены."
        
        return {
            "timeline": timeline,
            "analysis": analysis,
            "summary": summary,
            "data_source": "mock",
            "bank": bank,
            "product_type": product_type,
            "period": period
        }
