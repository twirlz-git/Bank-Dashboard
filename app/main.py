"""
main.py - Enhanced Streamlit application with wow-effect charts
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
from modules.llm_comparator import LLMComparator  # NEW
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
    st.session_state.comparator = ProductComparator()  # Legacy comparator
    st.session_state.llm_comparator = LLMComparator()  # NEW: LLM-powered comparator
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

# LLM Status indicator
if st.session_state.llm_comparator.is_enabled():
    st.sidebar.success("✅ LLM-сравнение активно")
    st.sidebar.caption(f"🤖 Модель: {st.session_state.llm_comparator.model}")
else:
    st.sidebar.warning("⚠️ LLM недоступен")
    st.sidebar.caption("🔑 Добавьте OPENAI_API_KEY")

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
            ["ВТБ", "Альфа", "Тинькофф", "Газпромбанк", "Локобанк", "МТС Банк", "Райффайзенбанк"]
        )
    
    with col2:
        product_type = st.selectbox(
            "Тип продукта",
            ["credit_card", "debit_card", "deposit", "consumer_loan"],
            format_func=lambda x: {
                "credit_card": "Кредитная карта",
                "debit_card": "Дебетовая карта",
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
            competitor_data = st.session_state.scraper.get_product_data(bank, product_type)
            sber_data = st.session_state.scraper.get_product_data("Сбер", product_type)
            if not competitor_data.get('карты') or not sber_data.get('карты'):
                st.error("Не удалось загрузить данные для сравнения. Проверьте файлы данных.")
                st.stop()
            competitor_card = competitor_data['карты'][0]
            sber_card = sber_data['карты'][0]
            use_llm = st.session_state.llm_comparator.is_enabled()
            if use_llm:
                with st.spinner("🤖 LLM анализирует данные..."):
                    comparison = st.session_state.llm_comparator.compare_products(
                        sber_card,
                        competitor_card,
                        product_type,
                        bank
                    )
            else:
                with st.spinner("Анализирую данные..."):
                    normalizer_func = {
                        "credit_card": st.session_state.normalizer.normalize_credit_card,
                        "debit_card": st.session_state.normalizer.normalize_deposit,
                        "deposit": st.session_state.normalizer.normalize_deposit,
                        "consumer_loan": st.session_state.normalizer.normalize_consumer_loan,
                    }.get(product_type)
                    if not normalizer_func:
                        st.error(f"Неподдерживаемый тип продукта: {product_type}")
                        st.stop()
                    competitor_normalized = normalizer_func(competitor_card, bank)
                    sber_normalized = normalizer_func(sber_card, "Сбер")
                    comparison = st.session_state.comparator.compare_products(
                        sber_normalized, competitor_normalized, product_type
                    )

        st.markdown("---")
        st.markdown("## Результаты анализа")
        if comparison.get("llm_powered", False):
            st.success("🤖 Сравнение сгенерировано с помощью LLM")
        else:
            st.info("📄 Базовое сравнение")
        st.markdown("### 📋 Сравнительная таблица")
        st.dataframe(comparison["comparison_table"], use_container_width=True)
        # Add wow-effect charts
        st.markdown("### 🌟 Вау-графики сравнения")
        radar_fig = st.session_state.chart_gen_enhanced.generate_radar_comparison(comparison)
        st.plotly_chart(radar_fig, use_container_width=True)
        heatmap_fig = st.session_state.chart_gen_enhanced.generate_heatmap_comparison(comparison)
        st.plotly_chart(heatmap_fig, use_container_width=True)
        st.markdown("### 📈 Базовый bar-chart")
        try:
            fig = st.session_state.chart_gen.generate_comparison_chart(comparison)
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.warning(f"Не удалось построить график: {e}")
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
        st.markdown("---")
        xlsx_file = st.session_state.report_gen.generate_xlsx_comparison(comparison)
        st.download_button(
            label="📥 Скачать XLSX отчет",
            data=xlsx_file,
            file_name=st.session_state.report_gen.get_filename("urgent", bank),
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
else:
    st.markdown("### Анализ трендов - Динамика продуктов")
    st.markdown("Посмотрите, как менялись условия продуктов за выбранный период")
    col1, col2, col3 = st.columns(3)
    with col1:
        bank = st.selectbox("Выберите банк", ["ВТБ", "Альфа", "Газпромбанк", "Локобанк", "МТС Банк", "Райффайзенбанк"])
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
        if trends.get("data_source") == "mock":
            st.warning("⚠️ Используются мок-данные для демонстрации")
        else:
            st.success("✅ Данные получены через web-search")
        st.markdown("### 📊 Сводка")
        st.info(trends["summary"])
        if trends.get("timeline"):
            st.markdown("### 🌟 Анимированный timeline и водопад изменений")
            animated_fig = st.session_state.chart_gen_enhanced.generate_animated_timeline(trends["timeline"], f"Динамика - {bank}")
            st.plotly_chart(animated_fig, use_container_width=True)
            waterfall_fig = st.session_state.chart_gen_enhanced.generate_waterfall_trends(trends["timeline"])
            st.plotly_chart(waterfall_fig, use_container_width=True)
            st.markdown("### 📈 Базовый график timeline")
            try:
                product_names = {
                    "credit_card": "Кредитной карты",
                    "deposit": "Вклада",
                    "consumer_loan": "Потребительского кредита"
                }
                product_name = product_names.get(product_type, product_type)
                fig1 = st.session_state.chart_gen.generate_timeline_chart(
                    trends["timeline"],
                    f"Динамика {product_name} - {bank}"
                )
                st.plotly_chart(fig1, use_container_width=True)
                if trends.get("analysis") and trends["analysis"].get("status") == "success":
                    st.markdown("### 🗓️ Детальный анализ")
                    fig2 = st.session_state.chart_gen.generate_trend_analysis_chart(
                        trends["timeline"],
                        trends["analysis"]
                    )
                    st.plotly_chart(fig2, use_container_width=True)
                    st.markdown("### 📊 Статистика")
                    col1, col2, col3, col4 = st.columns(4)
                    analysis = trends["analysis"]
                    with col1:
                        st.metric(
                            "Начальное значение",
                            f"{analysis.get('start_value', 0):.2f}%"
                        )
                    with col2:
                        st.metric(
                            "Конечное значение",
                            f"{analysis.get('end_value', 0):.2f}%",
                            delta=f"{analysis.get('total_change', 0):+.2f}%"
                        )
                    with col3:
                        st.metric(
                            "Среднее значение",
                            f"{analysis.get('average_value', 0):.2f}%"
                        )
                    with col4:
                        st.metric(
                            "Изменений",
                            f"{analysis.get('change_points', 0)}"
                        )
            except Exception as e:
                st.error(f"Не удалось построить графики: {e}")
            st.markdown("### 📋 Таблица изменений")
            import pandas as pd
            timeline_df = pd.DataFrame(trends["timeline"])
            st.dataframe(timeline_df, use_container_width=True)
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
