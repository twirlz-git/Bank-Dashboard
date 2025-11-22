# Project Overview

This project is the "Banking Product Analyzer MVP" (Minimum Viable Product), a Streamlit web application designed to automate and accelerate the analytical work of product analysts. Its primary goal is to generate comprehensive reports on competitor banking products, including trend analysis via web search, within 30 minutes.

The system addresses key challenges such as manual data collection, slow analysis for urgent requests, difficulty in integrating data from various sources, and the lack of a simple way to track product condition changes over time without a pre-existing historical database.

**Key Features (MVP v2.0):**

*   **Urgent Report Mode:** Quickly compares Sberbank's products (credit cards, deposits, consumer loans) with competitor offerings. It scrapes current conditions from official websites, loads Sberbank's reference data from `configs/sber_products.json`, compares them against a fixed schema, and generates a comparison table with insights and recommendations.
*   **Trends Analysis Mode:** Analyzes the dynamics of product conditions over a specified period. It reconstructs historical data by performing targeted web searches on financial news sources (e.g., `banki.ru/news`, `sravni.ru`) and uses an LLM to extract a timeline of changes. This allows for trend visualization and identification of change factors.

The application is built with Python and utilizes a modular architecture. Key technologies include:

*   **Streamlit:** For the interactive web interface.
*   **FastAPI:** (Implied backend framework for API endpoints, though `run.py` directly launches Streamlit).
*   **Playwright (or Requests & BeautifulSoup):** For robust web scraping of competitor data, including JavaScript-rendered content.
*   **Pandas:** For efficient data manipulation and comparison.
*   **OpenAI GPT-4 / Claude 3 (LLM):** For intelligent routing of requests, extracting historical data from web search snippets, and generating insights and recommendations.
*   **Openpyxl:** For exporting reports to XLSX format.

**Project Structure:**

*   `app/main.py`: The main Streamlit application entry point.
*   `configs/`: Contains configuration files for Sberbank product data (`sber_products.json`), data sources and selectors (`data_sources.py`), and fixed comparison schemas (`schemas.py`).
*   `modules/`: Houses the core logic components:
    *   `llm_router`: Routes user requests to the appropriate analysis mode.
    *   `scraper`: Handles web scraping of competitor product data.
    *   `normalizer`: Normalizes scraped data to a consistent format.
    *   `comparator`: Compares products and generates insights.
    *   `trends_analyzer`: Manages the web search and LLM-based historical data extraction for trend analysis.
    *   `report_generator`: Creates and exports reports in XLSX format.
    *   `utils`: Utility functions.

# Building and Running

To run the application, you need to have Python and the required dependencies installed.

1.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

2.  **Run the application:**

    ```bash
    python run.py
    ```

    The application will be available at `http://localhost:8501`.

# Development Conventions

*   **Hardcoded Sberbank Data:** Sberbank's product data is stored in `configs/sber_products.json` instead of a database. This simplifies the MVP by assuming internal access to Sberbank's offerings.
*   **Web Search for Historical Data:** For the Trends Analysis, historical product data is dynamically extracted from financial news websites via targeted web searches and LLM processing, rather than relying on a persistent historical database.
*   **Fixed Schemas:** Product comparisons adhere to predefined, fixed schemas for credit cards, deposits, and consumer loans. This ensures consistent data extraction by the LLM and simplifies report generation.
*   **Hardcoded Data Sources:** Web scraping URLs and CSS selectors for competitor banks and news sources are hardcoded in `configs/data_sources.py`.
*   **Modularity:** The codebase is organized into distinct modules, promoting clarity, maintainability, and extensibility.
*   **Error Handling:** The `scraper` module includes a fallback mechanism to provide mock data if web scraping encounters issues.
*   **Code Style:** Adherence to standard Python conventions (PEP 8).
*   **No Persistent Cache/Database (for MVP):** Redis and PostgreSQL are explicitly excluded from the MVP scope. Temporary data is held in memory within a single request, and the `cache/` folder is optional for debugging purposes.