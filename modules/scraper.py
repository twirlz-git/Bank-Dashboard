import json
import logging
from pathlib import Path
from typing import Dict, Any
import glob

logger = logging.getLogger(__name__)

BANK_CODE_MAP = {
    "ВТБ": "vtb",
    "Сбер": "sberbank",
    "Альфа": "alfabank",
    "Тинькофф": "tbank",
    "Газпромбанк": "gazprom",
    "Райффайзенбанк": "raif",
    "МТС Банк": "mts",
    "Локобанк": "loko"
}
PRODUCT_MAP = {
    "credit_card": "credit",
    "debit_card": "debit",
    "deposit": "deposit",
    "consumer_loan": "consumer_loan"
}

class BankDataReader:
    """Read product data from local JSON files"""

    def __init__(self):
        self.base_path = Path(__file__).parent.parent / "configs" / "bank_data"
    
    def get_product_data(self, bank: str, product_type: str) -> Dict[str, Any]:
        bcode = BANK_CODE_MAP.get(bank)
        ptype = PRODUCT_MAP.get(product_type)
        if bcode and ptype:
            # Pattern: *_bcode_ptype.json
            pattern = f"*_{bcode}_{ptype}.json"
            matches = list(self.base_path.glob(pattern))
            if matches:
                file_path = matches[0]
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        return json.load(f)
                except Exception as e:
                    logger.error(f"Error reading data file {file_path}: {e}")
                    return self._get_fallback_data(bank, product_type)
        logger.warning(f"No data file found for {bank} and {product_type}")
        return self._get_fallback_data(bank, product_type)

    def scrape_credit_card(self, bank: str, product_type: str = "credit_card") -> Dict[str, Any]:
        return self.get_product_data(bank, "credit_card")

    def scrape_deposit(self, bank: str) -> Dict[str, Any]:
        return self.get_product_data(bank, "deposit")

    def scrape_consumer_loan(self, bank: str) -> Dict[str, Any]:
        return self.get_product_data(bank, "consumer_loan")

    def scrape_debit_card(self, bank: str) -> Dict[str, Any]:
        return self.get_product_data(bank, "debit_card")

    def _get_fallback_data(self, bank: str, product_type: str) -> Dict[str, Any]:
        logger.info(f"Using fallback data for {bank} - {product_type}")
        mock_data = {
            "credit_card": {
                "банк": bank,
                "тип": "Кредитные карты",
                "карты": [{
                    "название": f"Кредитная карта {bank} (Fallback)",
                    "ставка": "N/A", "лимит": "N/A", "грейс_период": "N/A",
                }]
            },
            "debit_card": {
                "банк": bank,
                "тип": "Дебетовые карты",
                "карты": [{
                    "название": f"Дебетовая карта {bank} (Fallback)",
                    "стоимость": "N/A", "кешбек": "N/A",
                }]
            },
            "deposit": {
                "банк": bank,
                "тип": "Вклад",
                "карты": [{
                    "название": f"Вклад {bank} (Fallback)",
                    "ставка": "N/A", "срок": "N/A", "минимальный_взнос": "N/A",
                }]
            },
            "consumer_loan": {
                "банк": bank,
                "тип": "Потребительский кредит",
                "карты": [{
                    "название": f"Потребительский кредит {bank} (Fallback)",
                    "ставка": "N/A", "лимит": "N/A",
                }]
            }
        }
        return mock_data.get(product_type, {}).copy()
