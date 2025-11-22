"""
configs/field_mappings.py - Unified field mapping configuration

This module provides mappings between different data source field names
and the normalized schema fields used internally.
"""

from typing import Dict, List, Any

# ============================================================================
# FIELD MAPPINGS: Source field names → Normalized field names
# ============================================================================

CREDIT_CARD_FIELD_MAPPING = {
    # Standard fields from individual bank files
    "название": "product_name",
    "ставка": "interest_rate",
    "грейс_период": "grace_period",
    "кешбек": "cashback",
    "стоимость": "annual_fee",
    "лимит": "max_limit",
    "минимальный_платеж": "min_payment",
    
    # Fields from comparison files (different naming)
    "карта": "product_name",
    "кредитный_лимит": "max_limit",
    "стоимость_обслуживания": "annual_fee",
    "первоначальный_взнос": "initial_payment",
}

DEBIT_CARD_FIELD_MAPPING = {
    # Standard fields
    "название": "product_name",
    "стоимость": "annual_fee",
    "смс": "sms_notifications",
    "снятие_наличных": "cash_withdrawal",
    "переводы": "transfers",
    "процент": "interest_rate",
    "кешбек": "cashback",
    "программа_лояльности": "loyalty_program",
    "возраст": "age_requirement",
    "бонусы": "bonuses",
    
    # Fields from comparison files
    "карта": "product_name",
    "стоимость_обслуживания": "annual_fee",
    "смс_уведомления": "sms_notifications",
    "снятие_наличных_чужие_банки": "cash_withdrawal_other_banks",
    "переводы_по_реквизитам": "transfers_by_details",
    "процент_на_остаток": "interest_on_balance",
}

DEPOSIT_FIELD_MAPPING = {
    "название": "product_name",
    "ставка": "interest_rate",
    "срок": "term_months",
    "минимальная_сумма": "min_amount",
    "максимальная_сумма": "max_amount",
    "пополнение": "replenishment",
    "досрочное_снятие": "early_withdrawal",
    "страхование": "insurance",
}

CONSUMER_LOAN_FIELD_MAPPING = {
    "название": "product_name",
    "ставка": "interest_rate",
    "сумма": "max_amount",
    "лимит": "max_amount",
    "срок": "term_months",
    "комиссия": "commission",
    "время_одобрения": "approval_time",
}

# ============================================================================
# NESTED FIELD MAPPINGS: For complex nested structures
# ============================================================================

NESTED_FIELD_HANDLERS = {
    "снятие_наличных": {
        "в_банке_до_1млн": "cash_withdrawal_own_bank_under_1m",
        "в_банке_свыше_1млн": "cash_withdrawal_own_bank_over_1m",
        "другие_банки": "cash_withdrawal_other_banks",
    },
    "переводы": {
        "сбп_до_100к": "transfers_sbp_under_100k",
        "сбп_свыше_100к": "transfers_sbp_over_100k",
        "по_реквизитам": "transfers_by_details",
    },
    "грейс_период": {
        "покупки": "grace_period_purchases",
        "снятие_наличных": "grace_period_cash",
    },
}

# ============================================================================
# PRODUCT TYPE MAPPING
# ============================================================================

PRODUCT_TYPE_MAPPINGS = {
    "credit_card": CREDIT_CARD_FIELD_MAPPING,
    "debit_card": DEBIT_CARD_FIELD_MAPPING,
    "deposit": DEPOSIT_FIELD_MAPPING,
    "consumer_loan": CONSUMER_LOAN_FIELD_MAPPING,
}

# ============================================================================
# REVERSE MAPPINGS: For displaying data back in original format
# ============================================================================

def get_reverse_mapping(product_type: str) -> Dict[str, str]:
    """Get reverse mapping (normalized → original field names)"""
    forward_mapping = PRODUCT_TYPE_MAPPINGS.get(product_type, {})
    return {v: k for k, v in forward_mapping.items()}

# ============================================================================
# FIELD ALIASES: Alternative names for the same field
# ============================================================================

FIELD_ALIASES = {
    "interest_rate": ["ставка", "процентная_ставка", "процент_на_остаток"],
    "annual_fee": ["стоимость", "стоимость_обслуживания", "годовое_обслуживание"],
    "product_name": ["название", "карта", "название_продукта"],
    "max_limit": ["лимит", "кредитный_лимит", "максимальный_лимит"],
    "grace_period": ["грейс_период", "льготный_период"],
    "cashback": ["кешбек", "кэшбэк"],
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_mapping_for_product(product_type: str) -> Dict[str, str]:
    """Get field mapping for a specific product type"""
    return PRODUCT_TYPE_MAPPINGS.get(product_type, {})

def get_all_possible_field_names(normalized_field: str) -> List[str]:
    """Get all possible source field names for a normalized field"""
    aliases = FIELD_ALIASES.get(normalized_field, [])
    # Add reverse lookups from all product mappings
    all_names = set(aliases)
    for mapping in PRODUCT_TYPE_MAPPINGS.values():
        for source, target in mapping.items():
            if target == normalized_field:
                all_names.add(source)
    return list(all_names)

def normalize_field_name(source_field: str, product_type: str) -> str:
    """Convert source field name to normalized field name"""
    mapping = get_mapping_for_product(product_type)
    return mapping.get(source_field, source_field)
