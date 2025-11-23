"""
modules/multi_bank_comparator.py - Multi-bank comparison functionality

Compares multiple competitor banks against Sberbank as a reference.
"""
import logging
from typing import Dict, Any, List, Optional
import pandas as pd
import json
from pathlib import Path
from dotenv import load_dotenv

project_root = Path(__file__).parent.absolute()
env_path = project_root / '.env'
load_dotenv(dotenv_path=env_path, override=True)

logger = logging.getLogger(__name__)

class MultiBankComparator:
    """Compare multiple banks against Sberbank"""

    def __init__(self, llm_comparator=None):
        """
        Initialize multi-bank comparator.
        
        Args:
            llm_comparator: Optional LLMComparator instance for intelligent comparison
        """
        self.llm_comparator = llm_comparator

    def compare_multiple_banks(
        self,
        sber_data: Dict[str, Any],
        competitor_data_list: List[Dict[str, Any]],
        bank_names: List[str],
        product_type: str
    ) -> Dict[str, Any]:
        """
        Compare Sberbank product against multiple competitors.

        Args:
            sber_data: Sberbank product data (raw JSON)
            competitor_data_list: List of competitor product data (raw JSON)
            bank_names: List of competitor bank names
            product_type: Type of product (credit_card, deposit, etc.)

        Returns:
            Dict with comparison_table, insights, advantages, recommendation
        """
        if not competitor_data_list:
            return self._empty_comparison()

        # Extract comparison parameters using LLM if available
        if self.llm_comparator and self.llm_comparator.is_enabled():
            return self._llm_multi_comparison(
                sber_data,
                competitor_data_list,
                bank_names,
                product_type
            )
        else:
            return self._basic_multi_comparison(
                sber_data,
                competitor_data_list,
                bank_names
            )

    def _llm_multi_comparison(
        self,
        sber_data: Dict[str, Any],
        competitor_data_list: List[Dict[str, Any]],
        bank_names: List[str],
        product_type: str
    ) -> Dict[str, Any]:
        """
        Use LLM to intelligently compare multiple banks.
        """
        try:
            prompt = self._build_multi_comparison_prompt(
                sber_data,
                competitor_data_list,
                bank_names,
                product_type
            )

            response = self.llm_comparator.client.chat.completions.create(
                model=self.llm_comparator.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Вы - эксперт по банковским продуктам. Ваша задача - сравнить продукт Сбербанка с несколькими конкурентами и выделить ключевые параметры для сравнения. Отвечайте на русском языке в формате JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.3
            )

            result = json.loads(response.choices[0].message.content)
            logger.info(f"LLM multi-bank comparison: {len(result.get('parameters', []))} parameters found")

            # Create comparison table
            comparison_df = self._create_multi_bank_table(result, bank_names)

            # Generate insights
            insights = self._generate_multi_bank_insights(result, bank_names, product_type)

            return {
                "comparison_table": comparison_df,
                "insights": insights,
                "sber_advantages": result.get("sber_advantages", []),
                "competitor_highlights": result.get("competitor_highlights", {}),
                "recommendation": result.get("recommendation", "Требуется дополнительный анализ"),
                "llm_powered": True
            }

        except Exception as e:
            logger.error(f"LLM multi-bank comparison failed: {e}")
            return self._basic_multi_comparison(
                sber_data,
                competitor_data_list,
                bank_names
            )

    def _build_multi_comparison_prompt(
        self,
        sber_data: Dict[str, Any],
        competitor_data_list: List[Dict[str, Any]],
        bank_names: List[str],
        product_type: str
    ) -> str:
        """
        Build prompt for LLM to structure multi-bank comparison.
        """
        product_type_ru = {
            "credit_card": "кредитная карта",
            "debit_card": "дебетовая карта",
            "deposit": "вклад",
            "consumer_loan": "потребительский кредит",
        }.get(product_type, product_type)

        competitors_data = ""
        for i, (bank_name, data) in enumerate(zip(bank_names, competitor_data_list), 1):
            competitors_data += f"\n**Данные {bank_name}:**\n```json\n{json.dumps(data, ensure_ascii=False, indent=2)}\n```\n"

        return f"""Сравните продукт Сбербанка типа \"{product_type_ru}\" с несколькими конкурентами.

**Данные Сбербанка:**
```json
{json.dumps(sber_data, ensure_ascii=False, indent=2)}
```
{competitors_data}
**Задача:**
1. Извлеките все сравнимые параметры из всех продуктов
2. Для каждого параметра укажите значения для Сбера и всех конкурентов
3. Найдите преимущества Сбербанка
4. Найдите самые конкурентные предложения среди конкурентов
5. Дайте общую рекомендацию

**Верните JSON в следующем формате:**
{{
    "parameters": [
        {{
            "name": "Название параметра (на русском)",
            "sber_value": "Значение для Сбера",
            "competitor_values": {{
                "Банк1": "Значение",
                "Банк2": "Значение"
            }},
            "best_bank": "Название банка с лучшим значением или null"
        }}
    ],
    "sber_advantages": [
        "• Преимущество 1",
        "• Преимущество 2"
    ],
    "competitor_highlights": {{
        "Банк1": [
            "• Сильная сторона 1",
            "• Сильная сторона 2"
        ],
        "Банк2": [
            "• Сильная сторона 1"
        ]
    }},
    "recommendation": "Общая рекомендация по результатам сравнения (2-3 предложения)"
}}

**Правила:**
- Включите ВСЕ параметры, которые есть хотя бы в одном продукте
- Если параметра нет, используйте "Н/Д"
- Для процентных ставок: меньше = лучше для кредитов, больше = лучше для вкладов
- Для комиссий и стоимости: меньше = лучше
- Будьте объективны и конкретны
- Форматируйте текст используя Markdown:
  - Выделяйте ключевые цифры и названия жирным шрифтом (**текст**)
  - Используйте эмодзи, где уместно
"""

    def _create_multi_bank_table(
        self,
        comparison_structure: Dict[str, Any],
        bank_names: List[str]
    ) -> pd.DataFrame:
        """
        Create pandas DataFrame from multi-bank comparison structure.
        """
        parameters = comparison_structure.get("parameters", [])

        if not parameters:
            return pd.DataFrame({
                "Параметр": ["Нет данных"],
                "Сбербанк": ["Н/Д"],
                **{bank: ["Н/Д"] for bank in bank_names}
            })

        # Build table data
        table_data = {
            "Параметр": [p["name"] for p in parameters],
            "Сбербанк": [p["sber_value"] for p in parameters]
        }

        # Add columns for each competitor
        for bank_name in bank_names:
            table_data[bank_name] = [
                p["competitor_values"].get(bank_name, "Н/Д")
                for p in parameters
            ]

        df = pd.DataFrame(table_data)
        return df

    def _generate_multi_bank_insights(
        self,
        comparison_structure: Dict[str, Any],
        bank_names: List[str],
        product_type: str
    ) -> List[str]:
        """
        Generate insights from multi-bank comparison using LLM.
        """
        prompt = f"""На основе следующего многобанковского сравнения, сгенерируйте 4-6 ключевых выводов:

```json
{json.dumps(comparison_structure, ensure_ascii=False, indent=2)}
```

**Требования к выводам:**
- Краткие и конкретные (1 строка)
- Начинаются с ✓ (для позитивных) или ⚠️ (для предупреждений)
- Содержат конкретные цифры или факты
- Упоминают конкретные банки
- На русском языке
- Используйте Markdown форматирование:
  - Выделяйте банки, метрики и суммы жирным шрифтом (**текст**)

**Формат ответа (JSON):**
{{
    "insights": [
        "✓ Первый вывод",
        "⚠️ Второй вывод"
    ]
}}
"""

        try:
            response = self.llm_comparator.client.chat.completions.create(
                model=self.llm_comparator.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Вы - финансовый аналитик. Генерируйте краткие, информативные выводы о многобанковском сравнении."
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
            logger.error(f"Failed to generate multi-bank insights: {e}")
            return ["⚠️ Не удалось сгенерировать выводы"]

    def _basic_multi_comparison(
        self,
        sber_data: Dict[str, Any],
        competitor_data_list: List[Dict[str, Any]],
        bank_names: List[str]
    ) -> Dict[str, Any]:
        """
        Fallback to basic multi-bank comparison when LLM is unavailable.
        """
        # Get all unique keys from all datasets
        all_keys = set(sber_data.keys())
        for data in competitor_data_list:
            all_keys.update(data.keys())

        # Build comparison table
        table_data = {
            "Параметр": list(all_keys),
            "Сбербанк": [sber_data.get(k, "Н/Д") for k in all_keys]
        }

        # Add columns for each competitor
        for i, bank_name in enumerate(bank_names):
            table_data[bank_name] = [
                competitor_data_list[i].get(k, "Н/Д")
                for k in all_keys
            ]

        comparison_df = pd.DataFrame(table_data)

        return {
            "comparison_table": comparison_df,
            "insights": ["⚠️ LLM недоступен - базовое сравнение"],
            "sber_advantages": ["Требуется анализ с LLM"],
            "competitor_highlights": {bank: ["Требуется анализ с LLM"] for bank in bank_names},
            "recommendation": "LLM недоступен для генерации рекомендации",
            "llm_powered": False
        }

    def _empty_comparison(self) -> Dict[str, Any]:
        """
        Return empty comparison structure.
        """
        return {
            "comparison_table": pd.DataFrame({
                "Параметр": ["Нет данных"],
                "Сбербанк": ["Н/Д"]
            }),
            "insights": ["⚠️ Не выбраны банки для сравнения"],
            "sber_advantages": [],
            "competitor_highlights": {},
            "recommendation": "Выберите банки для сравнения",
            "llm_powered": False
        }
