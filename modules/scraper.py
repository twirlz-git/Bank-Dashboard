"""
modules/scraper.py - Data reader module for collecting current product data from local files
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)

class BankDataReader:
    """Read product data from local JSON files"""

    def __init__(self):
        self.base_path = Path(__file__).parent.parent / "configs" / "bank_data"
        self.file_mapping = {
            "credit_card": {
                "ВТБ": "4_vtb_credit.json",
                "Сбер": "6_sberbank_credit.json",
                "Альфа": "8_alfabank_credit.json",
                "Тинькофф": "10_tbank_credit.json",
            },
            "debit_card": {
                "ВТБ": "3_vtb_debit.json",
                "Сбер": "5_sberbank_debit.json",
                "Альфа": "7_alfabank_debit.json",
                "Тинькофф": "9_tbank_debit.json",
            }
        }

    def get_product_data(self, bank: str, product_type: str) -> Dict[str, Any]:
        """Load product data for a specific bank and product type"""
        file_name = self.file_mapping.get(product_type, {}).get(bank)
        if not file_name:
            logger.warning(f"No data file configured for {bank} and {product_type}")
            return self._get_fallback_data(bank, product_type)

        file_path = self.base_path / file_name
        if not file_path.exists():
            logger.error(f"Data file not found: {file_path}")
            return self._get_fallback_data(bank, product_type)

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error reading data file {file_path}: {e}")
            return self._get_fallback_data(bank, product_type)

    def scrape_credit_card(self, bank: str, product_type: str = "credit_card") -> Dict[str, Any]:
        """Get credit card data for a specific bank"""
        return self.get_product_data(bank, "credit_card")

    def scrape_deposit(self, bank: str) -> Dict[str, Any]:
        """Get deposit data for a specific bank"""
        # Assuming debit card files contain deposit-like info for now
        return self.get_product_data(bank, "debit_card")

    def _get_fallback_data(self, bank: str, product_type: str) -> Dict[str, Any]:
        """Return mock data when data loading fails"""
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
            "consumer_loan": {
                "банк": bank,
                "тип": "Потребительский кредит",
                "карты": [{
                    "название": f"Потребительский кредит {bank} (Fallback)",
                    "ставка": "N/A", "лимит": "N/A",
                }]
            }
        }
        # Return a copy to prevent modification of the original mock data
        return mock_data.get(product_type, {}).copy()

