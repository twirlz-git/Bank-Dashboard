"""
modules/trends_analyzer.py - Trends mode analysis through web search
"""

import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class TrendsAnalyzer:
    """Analyze product trends through web search and historical data"""
    
    def analyze_trends(self, bank: str, product_type: str, time_period: str) -> Dict[str, Any]:
        """
        Analyze trends for a product over time period.
        For MVP - use mock data based on time period
        """
        
        timeline = self._generate_mock_timeline(bank, product_type, time_period)
        
        return {
            "bank": bank,
            "product_type": product_type,
            "period": time_period,
            "timeline": timeline,
            "analysis": self._analyze_timeline(timeline),
            "trend_direction": self._get_trend_direction(timeline),
            "summary": self._generate_summary(bank, product_type, timeline)
        }
    
    def _generate_mock_timeline(self, bank: str, product_type: str, time_period: str) -> List[Dict]:
        """Generate mock timeline for MVP demonstration"""
        
        base_date = datetime.now()
        timeline = []
        
        if time_period == "last_3_months":
            days_back = 92
            dates = [base_date - timedelta(days=x) for x in range(0, days_back, 30)]
        elif time_period == "last_6_months":
            days_back = 180
            dates = [base_date - timedelta(days=x) for x in range(0, days_back, 30)]
        else:
            days_back = 365
            dates = [base_date - timedelta(days=x) for x in range(0, days_back, 90)]
        
        # Mock data patterns
        rates = [19.5, 18.9, 18.2, 17.8]
        reasons = ["Решение ЦБ", "Реакция конкуренции", "Маркетинг", "Стабилизация"]
        
        for idx, date in enumerate(reversed(dates)):
            timeline.append({
                "date": date.strftime("%Y-%m-%d"),
                "rate": rates[idx % len(rates)],
                "value": f"{rates[idx % len(rates)]}%",
                "reason": reasons[idx % len(reasons)],
                "confidence": 0.85
            })
        
        return timeline
    
    def _analyze_timeline(self, timeline: List[Dict]) -> Dict[str, Any]:
        """Analyze timeline for patterns"""
        
        if not timeline:
            return {"status": "no_data"}
        
        values = [t.get("rate") for t in timeline if t.get("rate")]
        
        if len(values) < 2:
            return {"status": "insufficient_data"}
        
        return {
            "start_value": values[0],
            "end_value": values[-1],
            "min_value": min(values),
            "max_value": max(values),
            "average_value": sum(values) / len(values),
            "change_points": len([v for v in values if v != values[0]])
        }
    
    def _get_trend_direction(self, timeline: List[Dict]) -> str:
        """Determine overall trend direction"""
        
        if not timeline or len(timeline) < 2:
            return "stable"
        
        values = [t.get("rate") for t in timeline if t.get("rate")]
        
        if len(values) < 2:
            return "stable"
        
        start = values[0]
        end = values[-1]
        
        if end > start * 1.02:
            return "increasing"
        elif end < start * 0.98:
            return "decreasing"
        else:
            return "stable"
    
    def _generate_summary(self, bank: str, product_type: str, timeline: List[Dict]) -> str:
        """Generate human-readable summary"""
        
        trend = self._get_trend_direction(timeline)
        analysis = self._analyze_timeline(timeline)
        
        if analysis.get("status") == "no_data":
            return f"Недостаточно данных для анализа {product_type} {bank}"
        
        summary = f"Анализ {product_type} банка {bank}:\n"
        summary += f"• Начальное значение: {analysis.get('start_value')}%\n"
        summary += f"• Конечное значение: {analysis.get('end_value')}%\n"
        summary += f"• Среднее значение: {analysis.get('average_value', 0):.2f}%\n"
        summary += f"• Тренд: {'📈 Растущий' if trend == 'increasing' else '📉 Падающий' if trend == 'decreasing' else '→ Стабильный'}\n"
        
        if len(timeline) > 1:
            change = analysis.get('end_value', 0) - analysis.get('start_value', 0)
            summary += f"• Изменение за период: {change:+.2f}%"
        
        return summary
