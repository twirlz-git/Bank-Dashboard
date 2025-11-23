"""
modules/normalizer.py - Normalize data from various sources to a unified schema.

This refactored version uses field mappings to handle inconsistencies between
individual bank files and comparison files.
"""

import logging
from typing import Dict, Any, Optional

from modules.utils import normalize_rate, extract_number
from configs.field_mappings import (
    get_mapping_for_product,
    get_all_possible_field_names,
    NESTED_FIELD_HANDLERS
)

logger = logging.getLogger(__name__)


class DataNormalizer:
    """Нормализация различных форматов данных к единой схеме."""

    def normalize_credit_card(self, raw_data: Dict[str, Any], bank: str) -> Dict[str, Any]:
        """Нормализация данных кредитной карты."""
        return self._normalize_with_mapping(raw_data, bank, "credit_card", {
            "product_name": self._get_product_name,
            "interest_rate": self._get_interest_rate,
            "grace_period": self._get_grace_period,
            "cashback": self._get_cashback,
            "annual_fee": self._get_annual_fee,
            "max_limit": self._get_max_limit,
            "min_payment": self._get_min_payment,
            "min_salary_requirement": lambda d: d.get("мин_зарплата", "Н/Д"),
            "commission": lambda d: d.get("комиссия", "Н/Д"),
        })

    def normalize_debit_card(self, raw_data: Dict[str, Any], bank: str) -> Dict[str, Any]:
        """
        Нормализация данных дебетовой карты.
        Дебетовые карты имеют процент на остаток вместо процентной ставки.
        """
        return self._normalize_with_mapping(raw_data, bank, "debit_card", {
            "product_name": self._get_product_name,
            "annual_fee": self._get_annual_fee,
            "interest_on_balance": self._get_interest_rate,  # Процент на остаток
            "cashback": self._get_cashback,
            "loyalty_program": lambda d: d.get("программа_лояльности", "Н/Д"),
            "sms_notifications": lambda d: d.get("смс", "Н/Д"),
            "withdrawals": self._get_withdrawals,
            "transfers": self._get_transfers,
            "monthly_limit": lambda d: d.get("лимит_месячный", "Н/Д"),
        })

    def normalize_deposit(self, raw_data: Dict[str, Any], bank: str) -> Dict[str, Any]:
        """
        Нормализация данных вклада.
        """
        return self._normalize_with_mapping(raw_data, bank, "deposit", {
            "product_name": self._get_product_name,
            "interest_rate": self._get_interest_rate,
            "term_months": lambda d: d.get("срок", "Н/Д"),
            "min_amount": lambda d: d.get("минимальная_сумма", "Н/Д"),
            "max_amount": lambda d: d.get("максимальная_сумма", "Н/Д"),
            "replenishment": lambda d: d.get("пополнение", "Н/Д"),
            "early_withdrawal": lambda d: d.get("досрочное_снятие", "Н/Д"),
            "insurance": lambda d: d.get("страхование", "Н/Д"),
        })

    def normalize_consumer_loan(self, raw_data: Dict[str, Any], bank: str) -> Dict[str, Any]:
        """
        Нормализация данных потребительского кредита.
        """
        return self._normalize_with_mapping(raw_data, bank, "consumer_loan", {
            "product_name": self._get_product_name,
            "interest_rate": self._get_interest_rate,
            "max_amount": self._get_max_limit,
            "term_months": lambda d: d.get("срок", "Н/Д"),
            "commission": lambda d: d.get("комиссия", "Н/Д"),
            "approval_time": lambda d: d.get("время_одобрения", "Н/Д"),
            "min_score": lambda d: d.get("мин_скор", "Н/Д"),
        })

    def _normalize_with_mapping(
        self,
        raw_data: Dict[str, Any],
        bank: str,
        product_type: str,
        field_extractors: Dict[str, callable]
    ) -> Dict[str, Any]:
        """
        Общая нормализация с использованием field mappings и extractors.
        
        Args:
            raw_data: Исходные данные из JSON файла
            bank: Название банка
            product_type: Тип продукта (credit_card, debit_card, deposit, и т.д.)
            field_extractors: Dict из field_name -> extraction_function
        
        Returns:
            Нормализованный dict с данными
        """
        normalized = {"bank": bank}
        
        for field_name, extractor in field_extractors.items():
            try:
                value = extractor(raw_data)
                normalized[field_name] = value if value is not None else "Н/Д"
            except Exception as e:
                logger.warning(f"Error extracting {field_name} for {bank}: {e}")
                normalized[field_name] = "Н/Д"
        
        return normalized

    def _get_field_value(self, data: Dict[str, Any], field_aliases: list) -> Any:
        """
        Получить значение поля, пробуя несколько возможных имен.
        
        Args:
            data: Исходные данные dict
            field_aliases: Список возможных имен полей
        
        Returns:
            Значение поля или None если не найдено
        """
        for alias in field_aliases:
            if alias in data:
                return data[alias]
        return None

    # ========================================================================
    # FIELD EXTRACTION METHODS
    # ========================================================================

    def _get_product_name(self, data: Dict[str, Any]) -> str:
        """Извлечь название продукта из различных полей."""
        name = self._get_field_value(data, ["название", "карта", "product_name"])
        return str(name) if name else "Н/Д"

    def _get_interest_rate(self, data: Dict[str, Any]) -> str:
        """Извлечь и отформатировать процентную ставку."""
        rate = self._get_field_value(data, [
            "ставка", 
            "процент", 
            "процент_на_остаток",
            "interest_rate"
        ])
        return self._format_rate(rate)

    def _get_grace_period(self, data: Dict[str, Any]) -> str:
        """Извлечь и отформатировать льготный период (обрабатывает dict и string)."""
        grace = self._get_field_value(data, ["грейс_период", "grace_period"])
        
        if isinstance(grace, dict):
            # Handle nested structure like {"покупки": "120 дней"}
            period = grace.get('покупки', grace.get('purchases', "Н/Д"))
            return self._format_period(period)
        
        return self._format_period(grace)

    def _get_cashback(self, data: Dict[str, Any]) -> str:
        """Извлечь и отформатировать кэшбэк."""
        cashback = self._get_field_value(data, ["кешбек", "cashback"])
        return self._format_cashback(cashback)

    def _get_annual_fee(self, data: Dict[str, Any]) -> str:
        """Извлечь и отформатировать годовую плату."""
        fee = self._get_field_value(data, [
            "стоимость",
            "стоимость_обслуживания",
            "annual_fee"
        ])
        return self._format_fee(fee)

    def _get_max_limit(self, data: Dict[str, Any]) -> str:
        """Извлечь и отформатировать максимальный лимит/сумму."""
        limit = self._get_field_value(data, [
            "лимит",
            "кредитный_лимит",
            "максимальный_лимит",
            "max_limit"
        ])
        return self._format_amount(limit)

    def _get_min_payment(self, data: Dict[str, Any]) -> str:
        """Извлечь минимальный платеж."""
        min_pay = self._get_field_value(data, [
            "минимальный_платеж",
            "min_payment"
        ])
        return str(min_pay) if min_pay else "Н/Д"

    def _get_withdrawals(self, data: Dict[str, Any]) -> str:
        """Извлечь информацию о снятии наличных."""
        withdrawals = self._get_field_value(data, ["снятие_наличных", "withdrawals"])
        if isinstance(withdrawals, dict):
            # Форматировать dict в читабельную строку
            parts = [f"{k}: {v}" for k, v in withdrawals.items()]
            return "; ".join(parts)
        return str(withdrawals) if withdrawals else "Н/Д"

    def _get_transfers(self, data: Dict[str, Any]) -> str:
        """Извлечь информацию о переводах."""
        transfers = self._get_field_value(data, ["переводы", "transfers"])
        if isinstance(transfers, dict):
            # Форматировать dict в читабельную строку
            parts = [f"{k}: {v}" for k, v in transfers.items()]
            return "; ".join(parts)
        return str(transfers) if transfers else "Н/Д"

    # ========================================================================
    # FORMATTING METHODS
    # ========================================================================

    def _format_rate(self, value: Any) -> str:
        """Форматировать процентную ставку с лучшей обработкой различных форматов."""
        if value is None or value == "Нет":
            return "Н/Д"
        
        value_str = str(value)
        
        # Handle ranges like "9.8% - 49.8%" or "17.9%-25.9%"
        if '-' in value_str:
            # Clean up spacing
            return value_str.replace(' ', '')
        
        # Handle "до X%" format
        if 'до' in value_str.lower() or 'up to' in value_str.lower():
            return value_str
        
        # Try to parse as number
        rate = normalize_rate(value_str)
        if rate is not None:
            return f"{rate}%"
        
        # Return as-is if can't parse
        return value_str

    def _format_grace_period(self, value: Any) -> str:
        """Форматировать льготный период, обрабатывая dict структуры."""
        if isinstance(value, dict):
            period = value.get('покупки', "Н/Д")
            return self._format_period(period)
        return self._format_period(value)

    def _format_period(self, value: Any) -> str:
        """Форматировать временной период (дни, месяцы, и т.д.)."""
        if value is None or value == "Н/Д":
            return "Н/Д"
        
        value_str = str(value)
        
        # Already formatted (contains "дней" or "days")
        if 'дн' in value_str.lower() or 'day' in value_str.lower():
            return value_str
        
        # Try to extract number and add "дней"
        try:
            days = int(extract_number(value_str) or value)
            return f"{days} дней"
        except (ValueError, TypeError):
            return value_str

    def _format_cashback(self, value: Any) -> str:
        """Форматировать кэшбэк с лучшей обработкой различных форматов."""
        if value is None:
            return "Н/Д"
        
        # Already a string, return as-is
        if isinstance(value, str):
            return value
        
        # Float - convert to percentage
        if isinstance(value, float):
            return f"до {value * 100:.0f}%"
        
        return str(value)

    def _format_fee(self, value: Any) -> str:
        """Форматировать плату с лучшей обработкой 'Бесплатно' и различных форматов."""
        if value is None:
            return "Н/Д"
        
        value_str = str(value).lower()
        
        # Check for free indicators
        if value == 0 or "бесплатно" in value_str or "free" in value_str:
            return "0₽"
        
        # Already has currency symbol
        if '₽' in str(value) or '₽' in str(value):
            return str(value)
        
        # Try to parse as number
        if isinstance(value, (int, float)):
            return f"{value}₽"
        
        # Return as-is for complex strings like "0-990 ₽/год"
        return str(value)

    def _format_amount(self, value: Any) -> str:
        """Форматировать денежную сумму с лучшей обработкой."""
        if value is None:
            return "Н/Д"
        
        value_str = str(value)
        
        # Already formatted (contains ₽ or has "До")
        if '₽' in value_str or 'До' in value_str or 'до' in value_str.lower():
            return value_str
        
        # Handle ranges with dash
        if '-' in value_str and not value_str.startswith('-'):
            return value_str.replace(' ', '')
        
        # Try to format as number with spaces
        try:
            amount = int(extract_number(value_str) or value)
            return f"{amount:,}₽".replace(',', ' ')
        except (ValueError, TypeError):
            return value_str

    def _format_bool(self, value: Any) -> str:
        """Форматировать булевы значения на русский."""
        if isinstance(value, bool):
            return "Да" if value else "Нет"
        
        if isinstance(value, str):
            val_lower = value.lower()
            if val_lower in ["true", "да", "yes", "включены"]:
                return "Да"
            if val_lower in ["false", "нет", "no"]:
                return "Нет"
        
        return "Н/Д"
