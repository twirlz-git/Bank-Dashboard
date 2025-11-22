"""
modules/comparator.py - Comparison and insights generation
"""

import logging
from typing import Dict, Any, List, Optional
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
    
    def _extract_rate(self, rate_str: str) -> Optional[float]:
        """Extract numeric rate from string, handles ranges."""
        if not rate_str or rate_str == "Н/Д":
            return None
        try:
            # If it's a range like "17.9% - 25.9%", take the first number
            if '-' in str(rate_str):
                rate_str = str(rate_str).split('-')[0]
            
            return float(str(rate_str).replace('%', '').replace('₽', '').strip())
        except (ValueError, TypeError):
            logger.warning(f"Could not extract rate from '{rate_str}'")
            return None

    def _find_advantages(self, first: Dict, second: Dict, product_type: str) -> List[str]:
        """Find competitive advantages of first vs second"""
        advantages = []
        
        # Interest rate comparison (lower is better for credit, higher for deposit)
        rate1 = self._extract_rate(first.get("interest_rate"))
        rate2 = self._extract_rate(second.get("interest_rate"))
        if rate1 is not None and rate2 is not None:
            if product_type == "credit_card" and rate1 < rate2:
                advantages.append(f"• Более низкая процентная ставка: {first.get('interest_rate')}")
            if product_type == "deposit" and rate1 > rate2:
                advantages.append(f"• Более высокая процентная ставка: {first.get('interest_rate')}")

        # Annual fee comparison (lower is better)
        fee1_str = str(first.get("annual_fee", "Н/Д")).replace('₽', '')
        fee2_str = str(second.get("annual_fee", "Н/Д")).replace('₽', '')
        try:
            fee1 = float(fee1_str)
            fee2 = float(fee2_str)
            if fee1 < fee2:
                advantages.append(f"• Более низкая стоимость обслуживания: {first.get('annual_fee')}")
        except (ValueError, TypeError):
            pass # Cannot compare fees if they are not numeric

        return advantages if advantages else ["Преимущества не найдены"]

    def _get_recommendation(self, sber_advantages: List[str], 
                           competitor_advantages: List[str]) -> str:
        """Generate recommendation based on advantages"""
        if len(sber_advantages) > len(competitor_advantages):
            return "Сбер имеет более конкурентное предложение"
        elif len(competitor_advantages) > len(sber_advantages):
            return "Конкурент имеет лучшие условия - рекомендуется пересмотреть"
        else:
            return "Условия примерно сопоставимы"