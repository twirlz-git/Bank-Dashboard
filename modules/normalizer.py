"""
modules/normalizer.py - Normalize scraped data to fixed schema format
"""

import logging
from typing import Dict, Any, Optional
from modules.utils import normalize_rate, extract_number

logger = logging.getLogger(__name__)

class DataNormalizer:
    """Normalize various data formats to fixed schema"""
    
    def normalize_credit_card(self, raw_data: Dict[str, Any], bank: str) -> Dict[str, Any]:
        """Normalize credit card data to fixed schema"""
        return {
            "bank": bank,
            "product_name": raw_data.get("product_name", "Н/Д"),
            "interest_rate": self._format_rate(raw_data.get("rate")),
            "grace_period": self._format_period(raw_data.get("grace_period")),
            "cashback": self._format_cashback(raw_data.get("cashback")),
            "annual_fee": self._format_fee(raw_data.get("annual_fee")),
            "min_salary_requirement": raw_data.get("min_salary", "Н/Д"),
            "max_limit": self._format_amount(raw_data.get("max_limit")),
            "commission": self._format_fee(raw_data.get("commission"))
        }
    
    def normalize_deposit(self, raw_data: Dict[str, Any], bank: str) -> Dict[str, Any]:
        """Normalize deposit data to fixed schema"""
        return {
            "bank": bank,
            "product_name": raw_data.get("product_name", "Н/Д"),
            "interest_rate": self._format_rate(raw_data.get("rate")),
            "term_months": raw_data.get("term_months", "Н/Д"),
            "min_amount": self._format_amount(raw_data.get("min_amount")),
            "max_amount": self._format_amount(raw_data.get("max_amount")),
            "replenishment": self._format_bool(raw_data.get("replenishment")),
            "early_withdrawal": self._format_bool(raw_data.get("early_withdrawal")),
            "insurance": self._format_bool(raw_data.get("insurance"))
        }
    
    def normalize_consumer_loan(self, raw_data: Dict[str, Any], bank: str) -> Dict[str, Any]:
        """Normalize consumer loan data to fixed schema"""
        return {
            "bank": bank,
            "product_name": raw_data.get("product_name", "Н/Д"),
            "interest_rate": self._format_rate(raw_data.get("rate")),
            "max_amount": self._format_amount(raw_data.get("max_amount")),
            "term_months": raw_data.get("term_months", "Н/Д"),
            "commission": self._format_fee(raw_data.get("commission")),
            "approval_time": raw_data.get("approval_time", "Н/Д"),
            "min_score": raw_data.get("min_score", "Н/Д")
        }
    
    def _format_rate(self, value: Any) -> str:
        """Format interest rate"""
        if value is None:
            return "Н/Д"
        rate = normalize_rate(str(value))
        return f"{rate}%" if rate is not None else "Н/Д"
    
    def _format_period(self, value: Any) -> str:
        """Format grace period in days"""
        if value is None:
            return "Н/Д"
        try:
            days = int(extract_number(str(value)) or value)
            return f"{days} дней"
        except (ValueError, TypeError):
            return str(value)
    
    def _format_cashback(self, value: Any) -> str:
        """Format cashback percentage"""
        if value is None:
            return "Н/Д"
        try:
            if isinstance(value, float):
                return f"{value * 100}%"
            return str(value)
        except (ValueError, TypeError):
            return "Н/Д"
    
    def _format_fee(self, value: Any) -> str:
        """Format fee"""
        if value is None or value == 0:
            return "0₽"
        return f"{value}₽" if isinstance(value, (int, float)) else str(value)
    
    def _format_amount(self, value: Any) -> str:
        """Format monetary amount"""
        if value is None:
            return "Н/Д"
        try:
            amount = int(extract_number(str(value)) or value)
            return f"{amount:,}₽".replace(',', ' ')
        except (ValueError, TypeError):
            return str(value)
    
    def _format_bool(self, value: Any) -> str:
        """Format boolean to Russian"""
        if isinstance(value, bool):
            return "Да" if value else "Нет"
        if isinstance(value, str):
            return "Да" if value.lower() in ["true", "да", "yes"] else "Нет"
        return "Н/Д"
