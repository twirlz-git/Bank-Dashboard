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