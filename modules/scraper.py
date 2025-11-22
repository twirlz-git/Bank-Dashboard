"""
modules/scraper.py - Web scraping module for collecting current product data
"""

import logging
import requests
from typing import Dict, Any, Optional
from bs4 import BeautifulSoup
from configs.data_sources import DATA_SOURCES

logger = logging.getLogger(__name__)

class WebScraper:
    """Scrape product data from bank websites"""
    
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def scrape_credit_card(self, bank: str, product_type: str = "credit_card") -> Dict[str, Any]:
        """Scrape credit card data for specific bank"""
        if bank not in DATA_SOURCES.get(product_type, {}):
            logger.warning(f"No source configured for {bank}")
            return self._get_fallback_data(bank, product_type)
        
        source = DATA_SOURCES[product_type][bank]
        return self._scrape_url(source["url"], source.get("selectors", {}), bank)
    
    def scrape_deposit(self, bank: str) -> Dict[str, Any]:
        """Scrape deposit data"""
        return self.scrape_credit_card(bank, product_type="deposit")
    
    def _scrape_url(self, url: str, selectors: Dict[str, str], bank: str) -> Dict[str, Any]:
        """Generic URL scraping with CSS selectors"""
        try:
            response = self.session.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            data = {
                "bank": bank,
                "product_name": f"{bank} Product",
                "source": url
            }
            
            for field_name, selector in selectors.items():
                try:
                    element = soup.select_one(selector)
                    if element:
                        data[field_name] = element.get_text(strip=True)
                except Exception as e:
                    logger.debug(f"Selector error for {field_name}: {e}")
            
            return data
        
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            return self._get_fallback_data(bank, "credit_card")
    
    def _get_fallback_data(self, bank: str, product_type: str) -> Dict[str, Any]:
        """Return mock data when scraping fails"""
        mock_data = {
            "credit_card": {
                "bank": bank,
                "product_name": f"Кредитная карта {bank}",
                "rate": 19.9,
                "grace_period": 55,
                "cashback": 0.02,
                "annual_fee": 0,
                "max_limit": 500000
            },
            "deposit": {
                "bank": bank,
                "product_name": f"Вклад {bank}",
                "rate": 10.5,
                "term_months": 12,
                "min_amount": 1000,
                "max_amount": 5000000,
                "replenishment": True
            }
        }
        return mock_data.get(product_type, mock_data["credit_card"])
