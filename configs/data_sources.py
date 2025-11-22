# Data sources configuration with URLs and CSS selectors

DATA_SOURCES = {
    "credit_card": {
        "vtb": {
            "url": "https://www.vtb.ru/personal/karty/kreditnye/",
            "selectors": {
                "rate": "span.rate-value",
                "grace_period": "span.grace-days",
                "cashback": "span.cashback-percent",
                "annual_fee": "span.annual-fee-value"
            },
            "timeout": 15
        },
        "alphabank": {
            "url": "https://www.alfabank.ru/products/cards/credit/",
            "selectors": {
                "rate": "[data-testid='interest-rate']",
                "grace_period": "[data-testid='grace-period']",
                "cashback": "[data-testid='cashback']",
                "annual_fee": "[data-testid='annual-fee']"
            },
            "timeout": 15
        },
        "gazprombank": {
            "url": "https://www.gazprombank.ru/retail/cards/credit/",
            "selectors": {
                "rate": ".product-rate",
                "grace_period": ".grace-period-value",
                "cashback": ".cashback-info",
                "annual_fee": ".fee-value"
            },
            "timeout": 15
        },
        "lokobank": {
            "url": "https://loko-bank.ru/cards/credit/",
            "selectors": {
                "rate": ".credit-rate",
                "grace_period": ".grace-period",
                "cashback": ".cashback-value",
                "annual_fee": ".annual-fee"
            },
            "timeout": 15
        },
        "mtsbank": {
            "url": "https://www.mtsbank.ru/chastnim-licam/karty/kreditnye/",
            "selectors": {
                "rate": ".interest-rate",
                "grace_period": ".grace-period-info",
                "cashback": ".cashback-percent",
                "annual_fee": ".service-fee"
            },
            "timeout": 15
        },
        "raiffeisenbank": {
            "url": "https://www.raiffeisen.ru/retail/cards/credit/",
            "selectors": {
                "rate": ".rate-value",
                "grace_period": ".grace-days",
                "cashback": ".cashback-info",
                "annual_fee": ".fee-amount"
            },
            "timeout": 15
        }
    },
    "deposit": {
        "vtb": {
            "url": "https://www.vtb.ru/personal/vklady/",
            "selectors": {
                "rate": ".deposit-rate-value",
                "min_amount": ".min-deposit-amount",
                "term": ".term-months"
            },
            "timeout": 15
        },
        "gazprombank": {
            "url": "https://www.gazprombank.ru/retail/deposits/",
            "selectors": {
                "rate": ".deposit-rate",
                "min_amount": ".min-amount",
                "term": ".deposit-term"
            },
            "timeout": 15
        },
        "lokobank": {
            "url": "https://loko-bank.ru/deposits/",
            "selectors": {
                "rate": ".rate-value",
                "min_amount": ".min-deposit",
                "term": ".term-value"
            },
            "timeout": 15
        },
        "mtsbank": {
            "url": "https://www.mtsbank.ru/chastnim-licam/vklady/",
            "selectors": {
                "rate": ".deposit-rate-value",
                "min_amount": ".minimum-amount",
                "term": ".deposit-period"
            },
            "timeout": 15
        },
        "raiffeisenbank": {
            "url": "https://www.raiffeisen.ru/retail/deposits/",
            "selectors": {
                "rate": ".rate-percent",
                "min_amount": ".min-sum",
                "term": ".deposit-term"
            },
            "timeout": 15
        }
    },
    "news_sources": {
        "banki_ru": "https://banki.ru/news/",
        "sravni_ru": "https://sravni.ru/novosti/",
        "kommersant_fin": "https://www.kommersant.ru/rubric/37"
    }
}

SEARCH_PATTERNS = {
    "rate_history": "История изменения ставок по {product} {bank}",
    "changes_news": "{bank} {product} изменение условий {period}",
    "conditions_update": "Новые условия {product} {bank}",
    "recent_changes": "{bank} обновила условия {product}"
}

TIME_FILTERS = {
    "last_3_months": "-92 days",
    "last_6_months": "-180 days",
    "last_year": "-365 days"
}