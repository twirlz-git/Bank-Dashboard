"""
main.py - Enhanced Streamlit application with PDF export, debit cards, confidence indicators, and Multi-bank comparison
"""

import os
import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.llm_router import LLMRouter
from modules.scraper import BankDataReader
from modules.normalizer import DataNormalizer
from modules.comparator import ProductComparator
from modules.llm_comparator import LLMComparator
from modules.multi_bank_comparator import MultiBankComparator  # NEW
from modules.trends_analyzer import TrendsAnalyzer
from modules.report_generator import ReportGenerator
from modules.chart_generator import ChartGenerator
from modules.chart_generator_enhanced import EnhancedChartGenerator
from modules.utils import load_json_config

# Configure page
st.set_page_config(
    page_title="Banking Analyzer MVP",
    page_icon="🏬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'router' not in st.session_state:
    st.session_state.router = LLMRouter()
    st.session_state.scraper = BankDataReader()
    st.session_state.normalizer = DataNormalizer()
    st.session_state.comparator = ProductComparator()
    st.session_state.llm_comparator = LLMComparator()
    st.session_state.multi_comparator = MultiBankComparator(st.session_state.llm_comparator)  # NEW
    st.session_state.trends_analyzer = TrendsAnalyzer()
    st.session_state.report_gen = ReportGenerator()
    st.session_state.chart_gen = ChartGenerator()
    st.session_state.chart_gen_enhanced = EnhancedChartGenerator()
    st.session_state.sber_products = load_json_config("configs/sber_products.json")

# Title
st.title("🏬 Banking Product Analyzer MVP")
st.markdown("*Анализ конкурентных банковских продуктов с помощью AI*")

# Sidebar
st.sidebar.markdown("## ⚙️ Настройки")

# LLM Status indicator with confidence
if st.session_state.llm_comparator.is_enabled():
    st.sidebar.success("✅ LLM-сравнение активно")
    st.sidebar.caption(f"🤖 Модель: {st.session_state.llm_comparator.model}")
    st.sidebar.caption("🎯 Высокая достоверность (90%+)")
else:
    st.sidebar.warning("⚠️ LLM недоступен")
    st.sidebar.caption("🔑 Добавьте OPENAI_API_KEY")
    st.sidebar.caption("🎯 Базовая достоверность (70%)")

# PDF export status
if st.session_state.report_gen.pdf_enabled:
    st.sidebar.success("📝 PDF экспорт доступен")
else:
    st.sidebar.warning("⚠️ PDF экспорт недоступен")
    st.sidebar.caption("pip install reportlab")

mode = st.sidebar.radio(
    "Выберите режим анализа",
    ["📊 Срочный отчет (Urgent)", "🔄 Мульти-банк сравнение", "📈 Анализ трендов (Trends)"]
)

# Main content
if "Urgent" in mode:
    ... # (оставляю без изменений --- срочный отчет)

elif "Мульти-банк" in mode:
    st.markdown("### Мульти-банк сравнение - Сбер vs. Конкуренты")
    st.markdown("Сравните продукт Сбербанка с несколькими конкурентами одновременно")

    product_type = st.selectbox(
        "Тип продукта",
        ["credit_card", "debit_card", "deposit", "consumer_loan"],
        format_func=lambda x: {
            "credit_card": "Кредитная карта",
            "debit_card": "Дебетовая карта",
            "deposit": "Вклад",
            "consumer_loan": "Потребительский кредит"
        }[x],
        key="multi_product_type"
    )

    available_banks = ["ВТБ", "Альфа", "Тинькофф", "Газпромбанк", "Локобанк", "МТС Банк", "Райффайзенбанк"]
    selected_banks = st.multiselect(
        "Конкуренты (можно выбрать несколько)",
        available_banks,
        default=["ВТБ", "Альфа"],
        help="Выберите от 1 до 7 банков для сравнения с Сбербанком"
    )
    
    analyze_btn = st.button("🔍 Сравнить с конкурентами", use_container_width=True)
    
    if analyze_btn:
        if not selected_banks:
            st.warning("⚠️ Пожалуйста, выберите хотя бы один банк для сравнения")
            st.stop()
        with st.spinner("Собираю данные по всем банкам..."):
            sber_data = st.session_state.scraper.get_product_data("Сбер", product_type)
            if not sber_data.get('карты'):
                st.error("Не удалось загрузить данные Сбербанка")
                st.stop()
            sber_card = sber_data['карты'][0]
            competitor_data_list = []
            valid_banks = []
            for bank in selected_banks:
                bank_data = st.session_state.scraper.get_product_data(bank, product_type)
                if bank_data.get('карты'):
                    competitor_data_list.append(bank_data['карты'][0])
                    valid_banks.append(bank)
                else:
                    st.warning(f"⚠️ Данные для {bank} недоступны - пропускаем")
            if not competitor_data_list:
                st.error("Не удалось загрузить данные ни одного конкурента")
                st.stop()
            
            with st.spinner("🤖 LLM анализирует все банки..."):
                comparison = st.session_state.multi_comparator.compare_multiple_banks(
                    sber_card,
                    competitor_data_list,
                    valid_banks,
                    product_type
                )

        st.markdown("---")
        st.markdown("## Результаты мульти-банк сравнения")
        if comparison.get("llm_powered", False):
            st.success(f"🤖 Сравнение {len(valid_banks)} банков сгенерировано с помощью LLM")
        else:
            st.info("📄 Базовое сравнение")
        st.markdown("### 📊 Сравнительная таблица")
        st.markdown("*Сбербанк в первой колонке, конкуренты - справа*")
        st.dataframe(comparison["comparison_table"], use_container_width=True)
        
        st.markdown("### 💡 Ключевые выводы")
        for insight in comparison["insights"]:
            st.markdown(insight)
        
        st.markdown("### ✅ Преимущества Сбербанка")
        for adv in comparison["sber_advantages"]:
            st.markdown(adv)
        
        st.markdown("### ⚡ Сильные стороны конкурентов")
        competitor_highlights = comparison.get("competitor_highlights", {})
        if competitor_highlights:
            cols = st.columns(len(valid_banks))
            for i, bank in enumerate(valid_banks):
                with cols[i]:
                    st.markdown(f"**{bank}**")
                    highlights = competitor_highlights.get(bank, [])
                    for highlight in highlights:
                        st.markdown(highlight)
        
        st.markdown("### 🎯 Общая рекомендация")
        st.info(comparison["recommendation"])
        
        st.markdown("---")
        st.markdown("### 📥 Экспорт результатов")
        st.info("Функция экспорта мульти-банк сравнений будет добавлена позже")

else:
    ... # (оставляю без изменений --- анализ трендов)

# Footer
st.markdown("---")
st.markdown(
    "*MVP Banking Product Analyzer - Quick analysis of competitor banking products*\n"
    "Made with ❤️ for hackathons"
)
