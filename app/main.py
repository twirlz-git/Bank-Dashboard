"""
main.py - Production-ready app with real data integration
"""

import os
import streamlit as st
import sys
import asyncio
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.llm_router import LLMRouter
from modules.normalizer import DataNormalizer
from modules.comparator import ProductComparator
from modules.llm_comparator import LLMComparator
from modules.report_generator import ReportGenerator
from modules.chart_generator import ChartGenerator
from modules.chart_generator_enhanced import EnhancedChartGenerator
from modules.utils import load_json_config

# Import REAL data modules
try:
    from modules.scraper_real import RealBankDataReader
    from modules.trends_analyzer_real import RealTrendsAnalyzer
    REAL_DATA_AVAILABLE = True
except ImportError as e:
    st.warning(f"⚠️ Реальные модули недоступны: {e}")
    from modules.scraper import BankDataReader
    from modules.trends_analyzer import TrendsAnalyzer
    REAL_DATA_AVAILABLE = False

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
    
    # Use REAL scrapers if available
    if REAL_DATA_AVAILABLE:
        st.session_state.scraper = RealBankDataReader()
        st.session_state.trends_analyzer = RealTrendsAnalyzer()
        st.session_state.using_real_data = True
    else:
        st.session_state.scraper = BankDataReader()
        st.session_state.trends_analyzer = TrendsAnalyzer()
        st.session_state.using_real_data = False
    
    st.session_state.normalizer = DataNormalizer()
    st.session_state.comparator = ProductComparator()
    st.session_state.llm_comparator = LLMComparator()
    st.session_state.report_gen = ReportGenerator()
    st.session_state.chart_gen = ChartGenerator()
    st.session_state.chart_gen_enhanced = EnhancedChartGenerator()
    st.session_state.sber_products = load_json_config("configs/sber_products.json")

# Title
st.title("🏬 Banking Product Analyzer MVP")
st.markdown("*Анализ конкурентных банковских продуктов с помощью AI*")

# Sidebar
st.sidebar.markdown("## ⚙️ Настройки")

# Data source indicator
if st.session_state.using_real_data:
    st.sidebar.success("✅ Реальные данные")
    st.sidebar.caption("🌐 Playwright + Perplexity API")
else:
    st.sidebar.warning("⚠️ Тестовый режим")
    st.sidebar.caption("💾 Используются мок-данные")

# LLM Status
if st.session_state.llm_comparator.is_enabled():
    st.sidebar.success("✅ LLM-сравнение активно")
    st.sidebar.caption(f"🤖 Модель: {st.session_state.llm_comparator.model}")
else:
    st.sidebar.warning("⚠️ LLM недоступен")
    st.sidebar.caption("🔑 Добавьте OPENAI_API_KEY")

mode = st.sidebar.radio(
    "Выберите режим",
    ["📊 Срочный отчет", "📈 Анализ трендов"]
)

# Async wrapper for real data calls
async def fetch_product_data_async(scraper, bank, product_type):
    """Async wrapper for scraper calls"""
    return await scraper.get_product_data(bank, product_type)

async def fetch_trends_async(analyzer, bank, product_type, period):
    """Async wrapper for trends analyzer"""
    return await analyzer.analyze_trends(bank, product_type, period)

# Main content
if "Срочный" in mode:
    st.markdown("### Срочный отчет - Сравнение продуктов")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        bank = st.selectbox(
            "Банк конкурент",
            ["ВТБ", "Альфа", "Тинькофф", "Газпромбанк", "Локобанк", "МТС Банк", "Райффайзенбанк"]
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
        analyze_btn = st.button("🔍 Анализировать", use_container_width=True)
    
    if analyze_btn:
        with st.spinner("🌐 Собираю реальные данные..."):
            # Fetch data (async if real, sync if mock)
            if st.session_state.using_real_data:
                competitor_data = asyncio.run(fetch_product_data_async(
                    st.session_state.scraper, bank, product_type
                ))
                sber_data = asyncio.run(fetch_product_data_async(
                    st.session_state.scraper, "Сбер", product_type
                ))
            else:
                competitor_data = st.session_state.scraper.get_product_data(bank, product_type)
                sber_data = st.session_state.scraper.get_product_data("Сбер", product_type)
            
            # Show data source
            source = competitor_data.get("source", "unknown")
            if source == "official_website":
                st.success("✅ Данные с официального сайта")
            elif source == "perplexity_search":
                st.info("🌐 Данные через Perplexity API")
            elif source == "mock_fallback":
                st.warning("⚠️ Реальные данные недоступны - используются тестовые")
            
            if not competitor_data.get('карты') or not sber_data.get('карты'):
                st.error("Не удалось загрузить данные")
                st.stop()
            
            competitor_card = competitor_data['карты'][0]
            sber_card = sber_data['карты'][0]
            
            # LLM comparison
            use_llm = st.session_state.llm_comparator.is_enabled()
            if use_llm:
                with st.spinner("🤖 LLM анализирует..."):
                    comparison = st.session_state.llm_comparator.compare_products(
                        sber_card, competitor_card, product_type, bank
                    )
            else:
                with st.spinner("Анализирую..."):
                    normalizer_func = {
                        "credit_card": st.session_state.normalizer.normalize_credit_card,
                        "deposit": st.session_state.normalizer.normalize_deposit,
                        "consumer_loan": st.session_state.normalizer.normalize_consumer_loan,
                    }.get(product_type)
                    competitor_normalized = normalizer_func(competitor_card, bank)
                    sber_normalized = normalizer_func(sber_card, "Сбер")
                    comparison = st.session_state.comparator.compare_products(
                        sber_normalized, competitor_normalized, product_type
                    )
        
        # Display results
        st.markdown("---")
        st.markdown("## Результаты")
        st.dataframe(comparison["comparison_table"], use_container_width=True)
        
        # WOW charts
        st.markdown("### 🌟 Вау-графики")
        radar_fig = st.session_state.chart_gen_enhanced.generate_radar_comparison(comparison)
        st.plotly_chart(radar_fig, use_container_width=True)
        heatmap_fig = st.session_state.chart_gen_enhanced.generate_heatmap_comparison(comparison)
        st.plotly_chart(heatmap_fig, use_container_width=True)
        
        st.markdown("### 💡 Ключевые выводы")
        for insight in comparison["insights"]:
            st.write(insight)
        
        col_adv1, col_adv2 = st.columns(2)
        with col_adv1:
            st.markdown("### ✅ Преимущества Сбера")
            for adv in comparison["sber_advantages"]:
                st.write(adv)
        with col_adv2:
            st.markdown(f"### ⚡ Преимущества {bank}")
            for adv in comparison["competitor_advantages"]:
                st.write(adv)
        
        st.markdown("### 🎯 Рекомендация")
        st.info(comparison["recommendation"])
        
        xlsx_file = st.session_state.report_gen.generate_xlsx_comparison(comparison)
        st.download_button(
            label="📥 Скачать XLSX",
            data=xlsx_file,
            file_name=st.session_state.report_gen.get_filename("urgent", bank),
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

else:  # Trends mode
    st.markdown("### Анализ трендов")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        bank = st.selectbox("Банк", ["ВТБ", "Альфа", "Газпромбанк", "Локобанк", "МТС Банк"])
    with col2:
        product_type = st.selectbox(
            "Продукт",
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
            "Период",
            ["last_3_months", "last_6_months", "last_year"],
            format_func=lambda x: {
                "last_3_months": "3 месяца",
                "last_6_months": "6 месяцев",
                "last_year": "1 год"
            }[x]
        )
    
    analyze_btn = st.button("📊 Анализировать", use_container_width=True)
    
    if analyze_btn:
        with st.spinner("🌐 Ищу изменения через web-search..."):
            if st.session_state.using_real_data:
                trends = asyncio.run(fetch_trends_async(
                    st.session_state.trends_analyzer, bank, product_type, period
                ))
            else:
                trends = st.session_state.trends_analyzer.analyze_trends(
                    bank, product_type, period
                )
        
        st.markdown("---")
        st.markdown("## Результаты")
        
        # Show data source
        if trends.get("data_source") == "real_search":
            st.success("✅ Реальные данные из web-search")
        else:
            st.warning("⚠️ Тестовые данные")
        
        st.info(trends["summary"])
        
        if trends.get("timeline"):
            st.markdown("### 🌟 WOW-графики")
            animated_fig = st.session_state.chart_gen_enhanced.generate_animated_timeline(
                trends["timeline"], f"{bank}"
            )
            st.plotly_chart(animated_fig, use_container_width=True)
            
            waterfall_fig = st.session_state.chart_gen_enhanced.generate_waterfall_trends(
                trends["timeline"]
            )
            st.plotly_chart(waterfall_fig, use_container_width=True)
            
            st.markdown("### 📋 Таблица")
            import pandas as pd
            st.dataframe(pd.DataFrame(trends["timeline"]), use_container_width=True)
        
        xlsx_file = st.session_state.report_gen.generate_xlsx_trends(trends)
        st.download_button(
            label="📥 Скачать XLSX",
            data=xlsx_file,
            file_name=st.session_state.report_gen.get_filename("trends", bank, product_type),
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

# Footer
st.markdown("---")
if st.session_state.using_real_data:
    st.markdown("🌟 *Production Mode: Real Data* | Made with ❤️ for hackathons")
else:
    st.markdown("💾 *Demo Mode: Mock Data* | Made with ❤️ for hackathons")
