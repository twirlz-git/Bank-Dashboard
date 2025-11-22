# Bank Dashboard - Real Data Integration Guide

Этот документ описывает, как запустить систему с **реальными данными** вместо моков.

---

## 🎯 Что реализовано

### Urgent Mode (Срочный отчет)
✅ **Playwright web scraping** - парсинг официальных сайтов банков  
✅ **Perplexity API fallback** - поиск через Perplexity если scraping упал  
✅ **OpenAI extraction** - извлечение данных через LLM  
✅ **Graceful degradation** - автоматический fallback на моки с предупреждением

### Trends Mode (Анализ трендов)
✅ **Perplexity real-time search** - поиск новостей о банках  
✅ **OpenAI timeline extraction** - извлечение структурированного timeline из текста  
✅ **Auto mock fallback** - генерация тестовых данных если поиск не вернул результатов

---

## 🔑 API Keys требуются

### Обязательные

**PERPLEXITY_API_KEY** - для web-search в Trends Mode  
Как получить:
1. Регистрация: https://www.perplexity.ai/  
2. Settings -> API -> Generate API Key  
3. Copy key

**OPENAI_API_KEY** - для LLM-extraction и comparison  
Как получить:
1. Регистрация: https://platform.openai.com/  
2. API Keys -> Create new secret key  
3. Copy key

### Опциональные

**ANTHROPIC_API_KEY** - альтернатива OpenAI (пока не реализовано)

---

## 🛠️ Установка

### 1. Клонировать репозиторий

```bash
git clone https://github.com/twirlz-git/Bank-Dashboard.git
cd Bank-Dashboard
git checkout feature/here_we_go_again
```

### 2. Установить зависимости

```bash
pip install -r requirements.txt

# Инициализировать Playwright
playwright install chromium
```

### 3. Настроить API keys

Создать `.env` файл в корне проекта:

```bash
# .env
PERPLEXITY_API_KEY=pplx-xxxxxxxxxxxxxxxxxxxxxxxx
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**ВАЖНО:** Не коммить `.env` в Git!

### 4. Запустить

```bash
streamlit run app/main.py
```

Или:

```bash
python run.py
```

---

## 🔄 Режимы работы

### Production Mode (реальные данные)

Если API keys настроены:
- ✅ Система использует `RealBankDataReader` и `RealTrendsAnalyzer`
- ✅ UI показывает "✅ Реальные данные"
- ✅ Источник данных указывается в UI

### Demo Mode (тестовые данные)

Если API keys отсутствуют:
- ⚠️ Система автоматически переключается на mock-данные
- ⚠️ UI показывает "⚠️ Тестовый режим"
- ⚠️ Работает без интернета

---

## 🌐 Как это работает

### Urgent Mode - Fallback Strategy

```
1. Playwright scraping официального сайта
   ↓ (если упало)
2. Perplexity API search
   ↓ (если упало)
3. OpenAI extraction
   ↓ (если упало)
4. Mock data + warning
```

**Пример реального запроса:**

```python
# modules/scraper_real.py

async def get_product_data(bank: str, product_type: str):
    # Try scraping official site
    data = await scrape_bank_website(bank, product_type)
    if data:
        return {"source": "official_website", "карты": [data]}
    
    # Fallback to Perplexity
    data = await fetch_via_perplexity(bank, product_type)
    if data:
        return {"source": "perplexity_search", "карты": [data]}
    
    # Last resort: mock
    return {"source": "mock_fallback", "карты": [mock_data]}
```

### Trends Mode - Search + Extract

```
1. Perplexity search: "Изменения условий {bank} {product} {period}"
   ↓
2. Получены новости + цитаты
   ↓
3. OpenAI извлекает timeline в JSON
   ↓
4. Визуализация графиков
```

**Пример extraction prompt:**

```
Извлеки все изменения условий банка ВТБ:

[текст новостей...]

Верни JSON:
[
  {"date": "2024-10-15", "rate": 25.5, "reason": "Повышение ключевой ставки ЦБ"},
  {"date": "2024-09-01", "rate": 24.0, "reason": "Плановое изменение"}
]
```

---

## 🔧 Конфигурация

### Добавить новый банк

Редактировать `configs/data_sources.py`:

```python
DATA_SOURCES = {
    "credit_card": {
        "newbank": {  # Новый банк
            "url": "https://newbank.ru/cards/credit/",
            "selectors": {
                "rate": ".interest-rate-value",
                "grace_period": ".grace-days",
                "cashback": ".cashback-percent"
            },
            "timeout": 15
        }
    }
}
```

### Обновить селекторы

Если банк поменял верстку сайта:

```python
DATA_SOURCES["credit_card"]["vtb"]["selectors"]["rate"] = ".new-rate-class"
```

Или использовать несколько селекторов (через запятую):

```python
"rate": ".rate-value, .interest-rate, [data-rate]"
```

---

## 📊 Примеры использования

### Сценарий 1: Срочное сравнение

1. Выберите банк: **ВТБ**
2. Выберите продукт: **Кредитная карта**
3. Нажмите **Анализировать**

**Результат:**
- ✅ Данные с официального сайта ВТБ
- 🌟 Radar + Heatmap графики
- 📊 Сравнение со Сбером
- 📥 XLSX отчет

### Сценарий 2: Анализ трендов

1. Выберите банк: **Альфа**
2. Выберите продукт: **Вклад**
3. Выберите период: **6 месяцев**
4. Нажмите **Анализировать**

**Результат:**
- 🌐 Поиск через Perplexity API
- 🤖 Извлечение timeline через OpenAI
- 🌟 Анимированный timeline + waterfall
- 📥 XLSX отчет

---

## ⚠️ Траблшутинг

### Проблема: Playwright не работает

```bash
# Переустановить Playwright
playwright install chromium

# Или со всеми зависимостями
playwright install-deps
playwright install chromium
```

### Проблема: Perplexity API ошибка 401

Проверьте API key:

```bash
echo $PERPLEXITY_API_KEY
# Должен начинаться с pplx-
```

### Проблема: Все источники упали

Система автоматически переключится на mock-данные с предупреждением:

⚠️ **Реальные данные недоступны - используются тестовые**

Это **нормальное поведение** - система продолжит работать.

### Проблема: Нет данных для банка

Добавьте конфиг в `configs/data_sources.py` (см. выше).

---

## 📌 Структура проекта

```
Bank-Dashboard/
├── app/
│   └── main.py                    # Основной UI (интегрирует real modules)
├── modules/
│   ├── scraper.py                # Старый mock scraper
│   ├── scraper_real.py           # ✅ НОВЫЙ: Real Playwright scraper
│   ├── trends_analyzer.py        # Старый mock analyzer
│   ├── trends_analyzer_real.py   # ✅ НОВЫЙ: Real Perplexity search
│   ├── chart_generator.py        # Базовые графики
│   └── chart_generator_enhanced.py # ✅ WOW-графики
├── configs/
│   ├── data_sources.py           # ✅ URLs + selectors
│   └── sber_products.json        # Данные Сбера (референс)
├── .env                          # API keys (не коммитить!)
├── requirements.txt
└── README_REAL_DATA.md           # Этот файл
```

---

## 🚀 Что дальше?

### Готово к использованию:
✅ Playwright scraping  
✅ Perplexity API integration  
✅ OpenAI extraction  
✅ WOW-effect charts  
✅ Graceful fallback  
✅ Auto-detection real/mock mode

### Возможные улучшения:
🔴 Кэширование результатов (Redis/in-memory)  
🔴 Rate limiting для API calls  
🔴 Retry logic с exponential backoff  
🔴 Добавить Anthropic Claude API  
🔴 Background tasks для scraping  
🔴 Webhook для автоматических обновлений

---

## 👥 Support

Вопросы? Проблемы? Откройте issue в GitHub!

**Made with ❤️ for hackathons**
