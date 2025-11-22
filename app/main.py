"""
app/main.py - Main Streamlit application entry point
"""

import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.llm_router import LLMRouter
from modules.scraper import BankDataReader
from modules.normalizer import DataNormalizer
from modules.comparator import ProductComparator
from modules.trends_analyzer import TrendsAnalyzer
from modules.report_generator import ReportGenerator
from modules.utils import load_json_config

# Configure page
st.set_page_config(
    page_title="Banking Analyzer MVP",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'router' not in st.session_state:
    st.session_state.router = LLMRouter()
    st.session_state.scraper = BankDataReader()
    st.session_state.normalizer = DataNormalizer()
    st.session_state.comparator = ProductComparator()
    st.session_state.trends_analyzer = TrendsAnalyzer()
    st.session_state.report_gen = ReportGenerator()
    st.session_state.sber_products = load_json_config("configs/sber_products.json")

# Title
st.title("🏦 Banking Product Analyzer MVP")
st.markdown("*Анализ конкурентных банковских продуктов с помощью AI*")

# Sidebar
st.sidebar.markdown("## ⚙️ Настройки")
mode = st.sidebar.radio(
    "Выберите режим анализа",
    ["📊 Срочный отчет (Urgent)", "📈 Анализ трендов (Trends)"]
)

# Main content
if "Urgent" in mode:
    st.markdown("### Срочный отчет - Сравнение продуктов")
    st.markdown("Быстро сравните банковские продукты с конкурентами")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        bank = st.selectbox(
            "Выберите банк конкурента",
            ["ВТБ", "Альфа", "Тинькофф"]
        )
    
    with col2:
        product_type = st.selectbox(
            "Тип продукта",
            ["credit_card", "deposit", "consumer_loan"],
            format_func=lambda x: {
                "credit_card": "Кредитная карта",
                "deposit": "Вклад",
                "consumer_loan": "Потребительский кредит"
            }[x]
        )
    
    with col3:
        st.write("")
        st.write("")
        analyze_btn = st.button("🔍 Анализировать", use_container_width=True)
    
    if analyze_btn:
        with st.spinner("Собираю данные..."):
            # Get competitor data from local files
            competitor_data = st.session_state.scraper.get_product_data(bank, product_type)
            
            # Get Sber reference data from local files
            sber_data = st.session_state.scraper.get_product_data("Сбер", product_type)

            # Select the correct normalization function based on product type
            normalizer_func = {
                "credit_card": st.session_state.normalizer.normalize_credit_card,
                "deposit": st.session_state.normalizer.normalize_deposit,
                "consumer_loan": st.session_state.normalizer.normalize_consumer_loan,
            }.get(product_type)
            
            if not normalizer_func:
                st.error(f"Неподдерживаемый тип продукта: {product_type}")
                st.stop()

            # Check if data was loaded successfully
            if not competitor_data.get('карты') or not sber_data.get('карты'):
                st.error("Не удалось загрузить данные для сравнения. Проверьте файлы данных.")
                st.stop()

            # Normalize data - using the first card for simplicity
            competitor_normalized = normalizer_func(competitor_data['карты'][0], bank)
            sber_normalized = normalizer_func(sber_data['карты'][0], "Сбер")
            
            # Compare
            comparison = st.session_state.comparator.compare_products(
                sber_normalized, competitor_normalized, product_type
            )
            
            # Display results
            st.markdown("---")
            st.markdown("## Результаты анализа")
            
            st.markdown("### 📋 Сравнительная таблица")
            st.dataframe(comparison["comparison_table"], use_container_width=True)
            
            st.markdown("### 💡 Ключевые выводы")
            for insight in comparison["insights"]:
                st.write(insight)
            
            st.markdown("### ✅ Преимущества Сбера")
            for adv in comparison["sber_advantages"]:
                st.write(adv)
            
            st.markdown("### ⚡ Преимущества конкурента")
            for adv in comparison["competitor_advantages"]:
                st.write(adv)
            
            st.markdown("### 🎯 Рекомендация")
            st.info(comparison["recommendation"])
            
            # Export button
            st.markdown("---")
            xlsx_file = st.session_state.report_gen.generate_xlsx_comparison(comparison)
            st.download_button(
                label="📥 Скачать XLSX отчет",
                data=xlsx_file,
                file_name=st.session_state.report_gen.get_filename("urgent", bank),
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

else:  # Trends mode
    st.markdown("### Анализ трендов - Динамика продуктов")
    st.markdown("Посмотрите, как менялись условия продуктов за выбранный период")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        bank = st.selectbox(
            "Выберите банк",
            ["ВТБ", "Альфа", "Газпром", "Райффайзен"]
        )
    
    with col2:
        product_type = st.selectbox(
            "Тип продукта",
            ["credit_card", "deposit", "consumer_loan"],
            format_func=lambda x: {
                "credit_card": "Кредитная карта",
                "deposit": "Вклад",
                "consumer_loan": "Потребительский кредит"
            }[x],
            key="trends_product"
        )
    
    with col3:
        period = st.selectbox(
            "Временной период",
            ["last_3_months", "last_6_months", "last_year"],
            format_func=lambda x: {
                "last_3_months": "Последние 3 месяца",
                "last_6_months": "Последние 6 месяцев",
                "last_year": "Последний год"
            }[x]
        )
    
    analyze_btn = st.button("📊 Анализировать тренды", use_container_width=True)
    
    if analyze_btn:
        with st.spinner("Анализирую тренды..."):
            trends = st.session_state.trends_analyzer.analyze_trends(
                bank, product_type, period
            )
            
            st.markdown("---")
            st.markdown("## Результаты анализа трендов")
            
            # Display summary
            st.markdown("### 📊 Сводка")
            st.info(trends["summary"])
            
            # Display timeline table
            if trends.get("timeline"):
                st.markdown("### 📅 Таблица изменений")
                import pandas as pd
                timeline_df = pd.DataFrame(trends["timeline"])
                st.dataframe(timeline_df, use_container_width=True)
            
            # Export button
            st.markdown("---")
            xlsx_file = st.session_state.report_gen.generate_xlsx_trends(trends)
            st.download_button(
                label="📥 Скачать XLSX отчет",
                data=xlsx_file,
                file_name=st.session_state.report_gen.get_filename("trends", bank, product_type),
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

# Footer
st.markdown("---")
st.markdown(
    "*MVP Banking Product Analyzer - Quick analysis of competitor banking products*\n"
    "Made with ❤️ for hackathons"
)
