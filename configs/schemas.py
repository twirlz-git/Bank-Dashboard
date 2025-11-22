"""
schemas.py - Fixed comparison schemas for different product types
"""

CREDIT_CARD_SCHEMA = {
    "type": "credit_card",
    "fields": [
        "bank",
        "product_name",
        "interest_rate",
        "grace_period",
        "cashback",
        "annual_fee",
        "min_salary_requirement",
        "max_limit",
        "commission"
    ],
    "display_names": {
        "bank": "Банк",
        "product_name": "Название продукта",
        "interest_rate": "Процентная ставка",
        "grace_period": "Льготный период",
        "cashback": "Кешбак",
        "annual_fee": "Годовое обслуживание",
        "min_salary_requirement": "Мин. зарплата",
        "max_limit": "Макс. лимит",
        "commission": "Комиссия"
    }
}

DEPOSIT_SCHEMA = {
    "type": "deposit",
    "fields": [
        "bank",
        "product_name",
        "interest_rate",
        "term_months",
        "min_amount",
        "max_amount",
        "replenishment",
        "early_withdrawal",
        "insurance"
    ],
    "display_names": {
        "bank": "Банк",
        "product_name": "Название продукта",
        "interest_rate": "Процентная ставка",
        "term_months": "Срок (месяцы)",
        "min_amount": "Мин. сумма",
        "max_amount": "Макс. сумма",
        "replenishment": "Пополнение",
        "early_withdrawal": "Ранний вывод",
        "insurance": "Страховка"
    }
}

CONSUMER_LOAN_SCHEMA = {
    "type": "consumer_loan",
    "fields": [
        "bank",
        "product_name",
        "interest_rate",
        "max_amount",
        "term_months",
        "commission",
        "approval_time",
        "min_score"
    ],
    "display_names": {
        "bank": "Банк",
        "product_name": "Название продукта",
        "interest_rate": "Процентная ставка",
        "max_amount": "Макс. сумма",
        "term_months": "Срок (месяцы)",
        "commission": "Комиссия",
        "approval_time": "Время одобрения",
        "min_score": "Мин. score"
    }
}

SCHEMAS = {
    "credit_card": CREDIT_CARD_SCHEMA,
    "deposit": DEPOSIT_SCHEMA,
    "consumer_loan": CONSUMER_LOAN_SCHEMA
}

def get_schema(product_type: str):
    """Get schema for product type"""
    return SCHEMAS.get(product_type, CREDIT_CARD_SCHEMA)
