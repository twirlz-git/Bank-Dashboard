"""
modules/llm_comparator.py - LLM-powered intelligent product comparison

Uses LLM to dynamically compare products based on actual available data,
rather than relying on hardcoded field mappings.
"""
import os
import json
import logging
from typing import Dict, Any, List, Optional
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv, find_dotenv

project_root = Path(__file__).parent.absolute()
env_path = project_root / '.env'
load_dotenv(dotenv_path=env_path, override=True)

logger = logging.getLogger(__name__)

class LLMComparator:
    """LLM-powered product comparator that adapts to available data"""

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        Initialize LLM comparator with OpenRouter support.
        Args:
            api_key: API key (defaults to OPENROUTER_API_KEY or OPENAI_API_KEY)
            base_url: API base URL (defaults to OpenRouter if not specified)
        """
        # Prioritize OpenRouter key, fall back to OpenAI key
        self.api_key = "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"
        # Default to OpenRouter if no base_url is provided
        self.base_url = "https://openrouter.ai/api/v1"
        self.model = "tngtech/deepseek-r1t2-chimera:free"
        # ------------------------

        if not self.api_key:
            logger.warning("No API key found. LLM comparison will be disabled.")
            self.enabled = False
        else:
            self.enabled = True
            try:
                from openai import OpenAI
                self.client = OpenAI(
                    api_key=self.api_key,
                    base_url=self.base_url
                )

                if "openrouter" in self.base_url.lower():
                    self.client.default_headers.update({
                        "HTTP-Referer": "https://github.com/twirlz-git/Bank-Dashboard",
                        "X-Title": "Banking Product Comparator"
                    })

            except ImportError:
                logger.error("openai package not installed. Run: pip install openai")
                self.enabled = False

    def compare_products(
        self,
        sber_data: Dict[str, Any],
        competitor_data: Dict[str, Any],
        product_type: str,
        competitor_name: str = "Конкурент"
    ) -> Dict[str, Any]:
        """
        Generate intelligent comparison using LLM.

        Args:
            sber_data: Sberbank product data (raw JSON)
            competitor_data: Competitor product data (raw JSON)
            product_type: Type of product (credit_card, deposit, etc.)
            competitor_name: Name of competitor bank

        Returns:
            Dict with comparison_table, insights, advantages, recommendation
        """
        if not self.enabled:
            logger.warning("LLM comparison disabled, falling back to basic comparison")
            return self._fallback_comparison(sber_data, competitor_data)

        try:
            # Step 1: Ask LLM to extract and structure comparison data
            comparison_structure = self._get_comparison_structure(
                sber_data, competitor_data, product_type, competitor_name
            )

            # Step 2: Ask LLM to generate insights
            insights = self._generate_llm_insights(
                comparison_structure, product_type, competitor_name
            )

            # Step 3: Create comparison dataframe
            comparison_df = self._create_comparison_table(comparison_structure)

            # Step 4: Extract advantages
            sber_advantages = comparison_structure.get("sber_advantages", [])
            competitor_advantages = comparison_structure.get("competitor_advantages", [])

            return {
                "comparison_table": comparison_df,
                "insights": insights,
                "sber_advantages": sber_advantages,
                "competitor_advantages": competitor_advantages,
                "recommendation": comparison_structure.get(
                    "recommendation", 
                    "Требуется дополнительный анализ"
                ),
                "llm_powered": True
            }

        except Exception as e:
            logger.error(f"LLM comparison failed: {e}")
            return self._fallback_comparison(sber_data, competitor_data)

    def _get_comparison_structure(
        self,
        sber_data: Dict[str, Any],
        competitor_data: Dict[str, Any],
        product_type: str,
        competitor_name: str
    ) -> Dict[str, Any]:
        """
        Ask LLM to extract comparable parameters and structure the comparison.
        """
        prompt = self._build_comparison_prompt(
            sber_data, competitor_data, product_type, competitor_name
        )

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "Вы - эксперт по банковским продуктам. Ваша задача - сравнить два продукта и выделить ключевые параметры для сравнения. Отвечайте на русском языке в формате JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            response_format={"type": "json_object"},
            temperature=0.3  # Lower temperature for more consistent output
        )

        result = json.loads(response.choices[0].message.content)
        logger.info(f"LLM comparison structure: {len(result.get('parameters', []))} parameters found")
        
        return result

    def _build_comparison_prompt(
        self,
        sber_data: Dict[str, Any],
        competitor_data: Dict[str, Any],
        product_type: str,
        competitor_name: str
    ) -> str:
        """
        Build prompt for LLM to structure the comparison.
        """
        product_type_ru = {
            "credit_card": "кредитная карта",
            "debit_card": "дебетовая карта",
            "deposit": "вклад",
            "consumer_loan": "потребительский кредит",
        }.get(product_type, product_type)

        return f"""Сравните два банковских продукта типа "{product_type_ru}".

**Данные Сбербанка:**
```json
{json.dumps(sber_data, ensure_ascii=False, indent=2)}
```

**Данные {competitor_name}:**
```json
{json.dumps(competitor_data, ensure_ascii=False, indent=2)}
```

**Задача:**
1. Извлеките все сравнимые параметры из обоих продуктов
2. Найдите преимущества каждого банка
3. Дайте рекомендацию

**Верните JSON в следующем формате:**
{{
    "parameters": [
        {{
            "name": "Название параметра (на русском)",
            "sber_value": "Значение для Сбера",
            "competitor_value": "Значение для конкурента",
            "is_better_for_sber": true/false/null
        }}
    ],
    "sber_advantages": [
        "• Преимущество 1",
        "• Преимущество 2"
    ],
    "competitor_advantages": [
        "• Преимущество 1",
        "• Преимущество 2"
    ],
    "recommendation": "Краткая рекомендация (1-2 предложения)"
}}

**Правила:**
- Включите ВСЕ параметры, которые есть хотя бы в одном продукте
- Если параметра нет, используйте "Н/Д"
- Для процентных ставок: меньше = лучше для кредитов, больше = лучше для вкладов
- Для комиссий и стоимости: меньше = лучше
- Будьте объективны и конкретны
- Форматируйте текст преимуществ и рекомендаций используя Markdown:
  - Выделяйте ключевые цифры и названия жирным шрифтом (**текст**)
  - Используйте эмодзи, где уместно
"""

    def _generate_llm_insights(
        self,
        comparison_structure: Dict[str, Any],
        product_type: str,
        competitor_name: str
    ) -> List[str]:
        """
        Ask LLM to generate key insights from the comparison.
        """
        prompt = f"""На основе следующего сравнения банковских продуктов, сгенерируйте 3-5 ключевых выводов:

```json
{json.dumps(comparison_structure, ensure_ascii=False, indent=2)}
```

**Требования к выводам:**
- Краткие и конкретные (1 строка)
- Начинаются с ✓ (для позитивных) или ⚠️ (для предупреждений)
- Содержат конкретные цифры или факты
- На русском языке
- Используйте Markdown форматирование для улучшения читаемости:
  - Выделяйте ключевые метрики и суммы жирным шрифтом (**текст**)

**Формат ответа (JSON):**
{{
    "insights": [
        "✓ Первый вывод",
        "⚠️ Второй вывод"
    ]
}}
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Вы - финансовый аналитик. Генерируйте краткие, информативные выводы."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.5
            )

            result = json.loads(response.choices[0].message.content)
            return result.get("insights", [])

        except Exception as e:
            logger.error(f"Failed to generate insights: {e}")
            return ["⚠️ Не удалось сгенерировать выводы"]

    def _create_comparison_table(self, comparison_structure: Dict[str, Any]) -> pd.DataFrame:
        """
        Create pandas DataFrame from comparison structure.
        """
        parameters = comparison_structure.get("parameters", [])
        
        if not parameters:
            return pd.DataFrame({
                "Параметр": ["Нет данных"],
                "Сбер": ["Н/Д"],
                "Конкурент": ["Н/Д"]
            })

        df = pd.DataFrame({
            "Параметр": [p["name"] for p in parameters],
            "Сбер": [p["sber_value"] for p in parameters],
            "Конкурент": [p["competitor_value"] for p in parameters]
        })
        
        return df

    def _fallback_comparison(
        self,
        sber_data: Dict[str, Any],
        competitor_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Fallback to basic comparison when LLM is unavailable.
        """
        # Get all unique keys from both datasets
        all_keys = set(sber_data.keys()) | set(competitor_data.keys())
        
        comparison_df = pd.DataFrame({
            "Параметр": list(all_keys),
            "Сбер": [sber_data.get(k, "Н/Д") for k in all_keys],
            "Конкурент": [competitor_data.get(k, "Н/Д") for k in all_keys]
        })
        
        return {
            "comparison_table": comparison_df,
            "insights": ["⚠️ LLM недоступен - базовое сравнение"],
            "sber_advantages": ["Требуется анализ"],
            "competitor_advantages": ["Требуется анализ"],
            "recommendation": "LLM недоступен для генерации рекомендации",
            "llm_powered": False
        }

    def is_enabled(self) -> bool:
        """Check if LLM comparison is available."""
        return self.enabled

    def set_model(self, model: str):
        """Change LLM model."""
        self.model = model
        logger.info(f"LLM model changed to: {model}")
