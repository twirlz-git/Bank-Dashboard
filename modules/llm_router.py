"""
modules/llm_router.py - LLM-based request routing to determine mode and parameters
"""

import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class LLMRouter:
    """Routes user requests to appropriate pipeline (urgent/trends)"""
    
    def __init__(self):
        self.request_types = ["urgent", "trends"]
        self.product_types = ["credit_card", "deposit", "consumer_loan"]
        self.banks = ["ВТБ", "Альфа", "Газпром", "Райффайзен"]
    
    def route_request(self, user_query: str) -> Dict[str, Any]:
        """
        Parse user query and determine:
        - request_type (urgent or trends)
        - product_type
        - banks involved
        - time_period (if trends)
        """
        
        query_lower = user_query.lower()
        
        # Detect request type
        request_type = self._detect_request_type(query_lower)
        
        # Detect product type
        product_type = self._detect_product_type(query_lower)
        
        # Detect banks
        banks = self._detect_banks(query_lower)
        
        # Detect time period (for trends)
        time_period = self._detect_time_period(query_lower) if request_type == "trends" else None
        
        return {
            "request_type": request_type,
            "product_type": product_type,
            "banks": banks,
            "time_period": time_period,
            "query": user_query,
            "confidence": self._calculate_confidence(request_type, product_type, banks)
        }
    
    def _detect_request_type(self, query: str) -> str:
        """Detect if user wants urgent comparison or trends analysis"""
        trends_keywords = ["история", "изменение", "тренд", "динамика", "как менялась", "за период", "последние"]
        urgent_keywords = ["новый", "вышел", "сравнить", "сравни", "отчет", "конкурент"]
        
        trends_count = sum(1 for kw in trends_keywords if kw in query)
        urgent_count = sum(1 for kw in urgent_keywords if kw in query)
        
        return "trends" if trends_count > urgent_count else "urgent"
    
    def _detect_product_type(self, query: str) -> str:
        """Detect product type from query"""
        product_keywords = {
            "credit_card": ["кредитная карта", "кредитка", "карта", "card"],
            "deposit": ["вклад", "депозит", "deposit"],
            "consumer_loan": ["кредит", "потребительский", "loan"]
        }
        
        for product_type, keywords in product_keywords.items():
            if any(kw in query for kw in keywords):
                return product_type
        
        return "credit_card"  # default
    
    def _detect_banks(self, query: str) -> list:
        """Extract bank names from query"""
        detected_banks = []
        for bank in self.banks:
            if bank.lower() in query:
                detected_banks.append(bank)
        return detected_banks if detected_banks else ["ВТБ"]  # default
    
    def _detect_time_period(self, query: str) -> str:
        """Detect time period for trends analysis"""
        if "3 месяца" in query or "3 месяцев" in query:
            return "last_3_months"
        elif "6 месяцев" in query:
            return "last_6_months"
        elif "год" in query:
            return "last_year"
        return "last_3_months"  # default
    
    def _calculate_confidence(self, request_type: str, product_type: str, banks: list) -> float:
        """Calculate confidence score for routing decision"""
        score = 0.5
        score += 0.2 if request_type in self.request_types else 0
        score += 0.2 if product_type in self.product_types else 0
        score += 0.1 if banks else 0
        return min(score, 1.0)
