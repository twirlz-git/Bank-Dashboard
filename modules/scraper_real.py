"""
modules/scraper_real.py - Real data scraping with Playwright and fallback strategies
"""

import asyncio
import logging
import os
import re
from typing import Dict, Any, Optional, List
import aiohttp
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout
from bs4 import BeautifulSoup
import json

try:
    from configs.data_sources import DATA_SOURCES
except:
    # Fallback if configs not in path
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from configs.data_sources import DATA_SOURCES

logger = logging.getLogger(__name__)


class RealBankDataReader:
    """Real web scraping implementation with multiple fallback strategies"""
    
    def __init__(self):
        self.perplexity_api_key = os.getenv("PERPLEXITY_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.timeout = 15000  # 15 seconds
    
    async def get_product_data(self, bank: str, product_type: str) -> Dict[str, Any]:
        """
        Main entry point - try multiple sources with graceful fallback
        
        Strategy:
        1. Try official bank website (Playwright)
        2. Try Perplexity API search
        3. Try OpenAI with web search
        4. Fallback to mock data with warning
        """
        
        bank_key = self._normalize_bank_name(bank)
        
        logger.info(f"Fetching {product_type} data for {bank}")
        
        # Strategy 1: Official bank website
        try:
            data = await self._scrape_bank_website(bank_key, product_type)
            if data and self._validate_data(data):
                logger.info(f"Successfully scraped from {bank} official site")
                return {
                    "карты": [data],
                    "source": "official_website",
                    "bank": bank,
                    "timestamp": self._get_timestamp()
                }
        except Exception as e:
            logger.warning(f"Official site scraping failed for {bank}: {e}")
        
        # Strategy 2: Perplexity API search
        if self.perplexity_api_key:
            try:
                data = await self._fetch_via_perplexity(bank, product_type)
                if data and self._validate_data(data):
                    logger.info(f"Successfully fetched from Perplexity API")
                    return {
                        "карты": [data],
                        "source": "perplexity_search",
                        "bank": bank,
                        "timestamp": self._get_timestamp()
                    }
            except Exception as e:
                logger.warning(f"Perplexity search failed: {e}")
        
        # Strategy 3: OpenAI with search (if available)
        if self.openai_api_key:
            try:
                data = await self._fetch_via_openai(bank, product_type)
                if data and self._validate_data(data):
                    logger.info(f"Successfully fetched via OpenAI")
                    return {
                        "карты": [data],
                        "source": "openai_search",
                        "bank": bank,
                        "timestamp": self._get_timestamp()
                    }
            except Exception as e:
                logger.warning(f"OpenAI search failed: {e}")
        
        # Fallback: Mock data with warning
        logger.error(f"All real data sources failed for {bank}, using mock data")
        return await self._get_mock_fallback(bank, product_type)
    
    async def _scrape_bank_website(self, bank_key: str, product_type: str) -> Optional[Dict[str, Any]]:
        """Scrape data from official bank website using Playwright"""
        
        source_config = DATA_SOURCES.get(product_type, {}).get(bank_key)
        
        if not source_config:
            logger.warning(f"No config for {bank_key} {product_type}")
            return None
        
        url = source_config['url']
        selectors = source_config['selectors']
        timeout = source_config.get('timeout', 15) * 1000
        
        logger.info(f"Scraping {url}")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            page = await context.new_page()
            
            try:
                # Navigate to page
                await page.goto(url, timeout=timeout, wait_until='networkidle')
                
                # Wait a bit for dynamic content
                await page.wait_for_timeout(2000)
                
                # Extract data
                data = {}
                
                for field, selector in selectors.items():
                    try:
                        # Try multiple selectors (comma-separated)
                        selector_list = [s.strip() for s in selector.split(',')]
                        
                        for sel in selector_list:
                            element = await page.query_selector(sel)
                            if element:
                                text = await element.text_content()
                                if text:
                                    data[field] = text.strip()
                                    break
                        
                        if field not in data:
                            data[field] = "Н/Д"
                            
                    except Exception as e:
                        logger.warning(f"Failed to extract {field}: {e}")
                        data[field] = "Н/Д"
                
                await browser.close()
                
                # Parse numeric values
                parsed_data = self._parse_scraped_data(data, product_type)
                return parsed_data
                
            except PlaywrightTimeout:
                logger.error(f"Timeout loading {url}")
                await browser.close()
                return None
            except Exception as e:
                logger.error(f"Scraping error: {e}")
                await browser.close()
                return None
    
    async def _fetch_via_perplexity(self, bank: str, product_type: str) -> Optional[Dict[str, Any]]:
        """Fetch product data via Perplexity API real-time search"""
        
        query = self._build_search_query(bank, product_type)
        
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {self.perplexity_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "sonar",
                "messages": [
                    {
                        "role": "system",
                        "content": "Ты эксперт по банковским продуктам. Верни только JSON с актуальными данными."
                    },
                    {
                        "role": "user",
                        "content": query
                    }
                ],
                "temperature": 0.1,
                "return_citations": True
            }
            
            try:
                async with session.post(
                    "https://api.perplexity.ai/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=20)
                ) as resp:
                    if resp.status != 200:
                        logger.error(f"Perplexity API error: {resp.status}")
                        return None
                    
                    result = await resp.json()
                    content = result['choices'][0]['message']['content']
                    
                    # Extract JSON from response
                    data = self._extract_json_from_text(content)
                    return data
                    
            except Exception as e:
                logger.error(f"Perplexity API call failed: {e}")
                return None
    
    async def _fetch_via_openai(self, bank: str, product_type: str) -> Optional[Dict[str, Any]]:
        """Fetch product data via OpenAI (with function calling)"""
        
        query = self._build_search_query(bank, product_type)
        
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {self.openai_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "gpt-4o-mini",
                "messages": [
                    {
                        "role": "system",
                        "content": "Ты эксперт по банковским продуктам России. Верни JSON с актуальными данными."
                    },
                    {
                        "role": "user",
                        "content": query
                    }
                ],
                "temperature": 0.1
            }
            
            try:
                async with session.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=20)
                ) as resp:
                    if resp.status != 200:
                        logger.error(f"OpenAI API error: {resp.status}")
                        return None
                    
                    result = await resp.json()
                    content = result['choices'][0]['message']['content']
                    
                    # Extract JSON
                    data = self._extract_json_from_text(content)
                    return data
                    
            except Exception as e:
                logger.error(f"OpenAI API call failed: {e}")
                return None
    
    def _build_search_query(self, bank: str, product_type: str) -> str:
        """Build search query for LLM"""
        
        product_names = {
            "credit_card": "кредитная карта",
            "debit_card": "дебетовая карта",
            "deposit": "вклад",
            "consumer_loan": "потребительский кредит"
        }
        
        product_ru = product_names.get(product_type, product_type)
        
        if product_type == "credit_card":
            query = f"""
            Найди актуальные условия {product_ru} банка {bank} на ноябрь 2024.
            
            Верни JSON:
            {{
                "название": "название карты",
                "банк": "{bank}",
                "процентная_ставка": число (напр. 24.9),
                "льготный_период": число дней,
                "кэшбэк": процент (0.03 = 3%),
                "годовое_обслуживание": число в рублях,
                "макс_лимит": число
            }}
            
            Используй только актуальные данные из официальных источников.
            """
        elif product_type == "deposit":
            query = f"""
            Найди актуальные условия {product_ru} банка {bank} на ноябрь 2024.
            
            Верни JSON:
            {{
                "название": "название вклада",
                "банк": "{bank}",
                "процентная_ставка": число,
                "мин_сумма": число,
                "срок": число месяцев
            }}
            """
        else:
            query = f"Найди актуальные условия {product_ru} {bank} в формате JSON"
        
        return query
    
    def _parse_scraped_data(self, raw_data: Dict[str, str], product_type: str) -> Dict[str, Any]:
        """Parse and normalize scraped text data"""
        
        parsed = {}
        
        for key, value in raw_data.items():
            if value == "Н/Д":
                parsed[key] = value
                continue
            
            # Extract numbers from text
            numbers = re.findall(r'\d+\.?\d*', value)
            
            if numbers:
                # Use first number found
                parsed[key] = float(numbers[0])
            else:
                parsed[key] = value
        
        return parsed
    
    def _extract_json_from_text(self, text: str) -> Optional[Dict[str, Any]]:
        """Extract JSON object from LLM response text"""
        
        try:
            # Try direct JSON parse
            return json.loads(text)
        except:
            pass
        
        # Try to find JSON in code block
        json_match = re.search(r'```json\s*({.*?})\s*```', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except:
                pass
        
        # Try to find any JSON object
        json_match = re.search(r'{.*}', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except:
                pass
        
        logger.error(f"Failed to extract JSON from: {text[:200]}")
        return None
    
    def _validate_data(self, data: Optional[Dict[str, Any]]) -> bool:
        """Validate that scraped data has required fields"""
        
        if not data:
            return False
        
        # Check if has at least one useful field
        useful_fields = ['процентная_ставка', 'rate', 'кэшбэк', 'cashback']
        
        for field in useful_fields:
            if field in data and data[field] != "Н/Д":
                return True
        
        return False
    
    async def _get_mock_fallback(self, bank: str, product_type: str) -> Dict[str, Any]:
        """Return mock data as last resort fallback"""
        
        mock_data = {
            "название": f"{bank} {product_type}",
            "банк": bank,
            "процентная_ставка": 25.0,
            "льготный_период": 120,
            "кэшбэк": 0.03,
            "годовое_обслуживание": 0
        }
        
        return {
            "карты": [mock_data],
            "source": "mock_fallback",
            "bank": bank,
            "warning": "⚠️ Реальные данные недоступны. Используются тестовые данные.",
            "timestamp": self._get_timestamp()
        }
    
    def _normalize_bank_name(self, bank: str) -> str:
        """Normalize bank name to config key"""
        
        mapping = {
            "втб": "vtb",
            "альфа": "alphabank",
            "альфа-банк": "alphabank",
            "тинькофф": "tinkoff",
            "газпромбанк": "gazprombank",
            "локобанк": "lokobank",
            "мтс банк": "mtsbank",
            "райффайзенбанк": "raiffeisenbank"
        }
        
        bank_lower = bank.lower().strip()
        return mapping.get(bank_lower, bank_lower.replace(" ", "").replace("-", ""))
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
