"""
modules/comparator.py - Comparison and insights generation
"""

import logging
from typing import Dict, Any, List
import pandas as pd

logger = logging.getLogger(__name__)

class ProductComparator:
    """Compare products and generate insights"""
    
    def compare_products(self, sber_data: Dict[str, Any], 
                        competitor_data: Dict[str, Any],
                        product_type: str) -> Dict[str, Any]:
        """Generate comparison report"""
        
        # Create comparison dataframe
        comparison_df = pd.DataFrame({
            "Параметр": list(sber_data.keys()),
            "Сбер": list(sber_data.values()),
            "Конкурент": [competitor_data.get(k, "Н/Д") for k in sber_data.keys()]
        })
        
        # Generate insights
        insights = self._generate_insights(sber_data, competitor_data, product_type)
        
        # Find advantages
        sber_advantages = self._find_advantages(sber_data, competitor_data, product_type)
        competitor_advantages = self._find_advantages(competitor_data, sber_data, product_type)
        
        return {
            "comparison_table": comparison_df,
            "insights": insights,
            "sber_advantages": sber_advantages,
            "competitor_advantages": competitor_advantages,
            "recommendation": self._get_recommendation(sber_advantages, competitor_advantages)
        }
    
    def _generate_insights(self, sber: Dict, competitor: Dict, product_type: str) -> List[str]:
        """Generate key insights from comparison"""
        insights = []
        
        if product_type == "credit_card":
            # Compare rates
            sber_rate = self._extract_rate(sber.get("interest_rate"))
            comp_rate = self._extract_rate(competitor.get("interest_rate"))
            
            if sber_rate and comp_rate:
                diff = comp_rate - sber_rate
                if abs(diff) < 0.1:
                    insights.append("✓ Процентные ставки практически идентичны")
                elif diff > 0:
                    insights.append(f"✓ Сбер выигрывает по ставке на {diff:.1f}%")
                else:
                    insights.append(f"⚠️ Конкурент выигрывает по ставке на {-diff:.1f}%")
        
        elif product_type == "deposit":
            sber_rate = self._extract_rate(sber.get("interest_rate"))
            comp_rate = self._extract_rate(competitor.get("interest_rate"))
            
            if sber_rate and comp_rate:
                diff = sber_rate - comp_rate
                if diff > 0:
                    insights.append(f"✓ Сбер предлагает выше ставку на {diff:.1f}%")
                elif diff < -0.5:
                    insights.append(f"⚠️ Конкурент выигрывает по ставке на {-diff:.1f}%")
        
        return insights
    
    def _find_advantages(self, first: Dict, second: Dict, product_type: str) -> List[str]:
        """Find competitive advantages of first vs second"""
        advantages = []
        
        # Common advantages check
        for key, value in first.items():
            second_value = second.get(key)
            if value != second_value and value != "Н/Д":
                if key in ["interest_rate", "commission", "annual_fee"]:
                    # Lower is better
                    if isinstance(value, str) and isinstance(second_value, str):
                        try:
                            if float(value.replace('%', '').replace('₽', '')) < \
                               float(second_value.replace('%', '').replace('₽', '')):
                                advantages.append(f"• {key}: {value}")
                        except:
                            pass
        
        return advantages if advantages else ["Данные не полны для детального анализа"]
    
    def _get_recommendation(self, sber_advantages: List[str], 
                           competitor_advantages: List[str]) -> str:
        """Generate recommendation based on advantages"""
        if len(sber_advantages) > len(competitor_advantages):
            return "Сбер имеет более конкурентное предложение"
        elif len(competitor_advantages) > len(sber_advantages):
            return "Конкурент имеет лучшие условия - рекомендуется пересмотреть"
        else:
            return "Условия примерно сопоставимы"
    
    def _extract_rate(self, rate_str: str) -> float:
        """Extract numeric rate from string"""
        if not rate_str or rate_str == "Н/Д":
            return None
        try:
            return float(str(rate_str).replace('%', '').replace('₽', '').strip())
        except:
            return None
