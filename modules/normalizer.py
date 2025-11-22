"""
modules/normalizer.py - Normalize data from local JSON files to a fixed schema format.
"""

import logging
from typing import Dict, Any

from modules.utils import normalize_rate, extract_number

logger = logging.getLogger(__name__)


class DataNormalizer:
    """Normalize various data formats to a fixed schema."""

    def normalize_credit_card(self, raw_data: Dict[str, Any], bank: str) -> Dict[str, Any]:
        """Normalize credit card data from the new JSON structure."""
        return {
            "bank": bank,
            "product_name": raw_data.get("название", "Н/Д"),
            "interest_rate": self._format_rate(raw_data.get("ставка")),
            "grace_period": self._format_grace_period(raw_data.get("грейс_период")),
            "cashback": self._format_cashback(raw_data.get("кешбек", "Н/Д")),
            "annual_fee": self._format_fee(raw_data.get("стоимость")),
            "max_limit": self._format_amount(raw_data.get("лимит")),
            "min_payment": raw_data.get("минимальный_платеж", "Н/Д"),
            "min_salary_requirement": "Н/Д",
            "commission": "Н/Д",
        }

    def normalize_deposit(self, raw_data: Dict[str, Any], bank: str) -> Dict[str, Any]:
        """
        Normalize deposit data to a fixed schema.
        Uses debit card data as a source for the MVP.
        """
        return {
            "bank": bank,
            "product_name": raw_data.get("название", "Н/Д"),
            "interest_rate": self._format_rate(raw_data.get("процент")),
            "annual_fee": self._format_fee(raw_data.get("стоимость")),
            "cashback": self._format_cashback(raw_data.get("кешбек")),
            "loyalty_program": raw_data.get("программа_лояльности", "Н/Д"),
            "term_months": "Н/Д",
            "min_amount": "Н/Д",
            "max_amount": "Н/Д",
            "replenishment": "Н/Д",
            "early_withdrawal": "Н/Д",
            "insurance": "Н/Д",
        }

    def normalize_consumer_loan(self, raw_data: Dict[str, Any], bank: str) -> Dict[str, Any]:
        """
        Normalize consumer loan data to a fixed schema.
        Assumes a structure similar to other JSON files.
        """
        return {
            "bank": bank,
            "product_name": raw_data.get("название", "Н/Д"),
            "interest_rate": self._format_rate(raw_data.get("ставка")),
            "max_amount": self._format_amount(raw_data.get("лимит")),
            "term_months": "Н/Д",
            "commission": "Н/Д",
            "approval_time": "Н/Д",
            "min_score": "Н/Д",
        }

    def _format_rate(self, value: Any) -> str:
        """Format interest rate"""
        if value is None or value == "Нет":
            return "Н/Д"
        if isinstance(value, str) and '-' in value:
            return value.replace(' ', '')
        rate = normalize_rate(str(value))
        return f"{rate}%" if rate is not None else "Н/Д"

    def _format_grace_period(self, value: Any) -> str:
        """Format grace period, which can be a dict"""
        if isinstance(value, dict):
            period = value.get('покупки', 'Н/Д')
            return self._format_period(period)
        return self._format_period(value)

    def _format_period(self, value: Any) -> str:
        """Format period in days"""
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
        if isinstance(value, float):
            return f"до {value * 100:.0f}%"
        return str(value)

    def _format_fee(self, value: Any) -> str:
        """Format fee"""
        if value is None or value == 0 or str(value).lower() == "бесплатно":
            return "0₽"
        return f"{value}₽" if isinstance(value, (int, float)) else str(value)

    def _format_amount(self, value: Any) -> str:
        """Format monetary amount"""
        if value is None:
            return "Н/Д"
        if isinstance(value, str) and '-' in value:
            return value.replace(' ', '')
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
            val_lower = value.lower()
            if val_lower in ["true", "да", "yes", "включены"]:
                return "Да"
            if val_lower in ["false", "нет", "no"]:
                return "Нет"
        return "Н/Д"

