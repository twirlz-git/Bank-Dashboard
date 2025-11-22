# New Banks Integration

## Summary

This update adds support for four new Russian banks to the Bank Dashboard comparison system:

- **Газпромбанк** (Gazprombank)
- **Локобанк** (Lokobank) 
- **МТС Банк** (MTS Bank)
- **Райффайзенбанк** (Raiffeisenbank)

## Changes Made

### 1. Data Configuration (`configs/data_sources.py`)

Added web scraping configurations for all four new banks:

- **Credit Card endpoints** with CSS selectors for:
  - Interest rates
  - Grace periods
  - Cashback programs
  - Annual fees
  
- **Deposit endpoints** with selectors for:
  - Interest rates
  - Minimum deposit amounts
  - Deposit terms

### 2. User Interface (`app/main.py`)

#### Urgent Report Mode
Updated bank selection dropdown to include:
```python
["ВТБ", "Альфа", "Тинькофф", "Газпромбанк", "Локобанк", "МТС Банк", "Райффайзенбанк"]
```

#### Trends Analysis Mode
Updated bank selection dropdown to include:
```python
["ВТБ", "Альфа", "Газпромбанк", "Локобанк", "МТС Банк", "Райффайзенбанк"]
```

### 3. Bank Data Files

The following data files were already added in `configs/bank_data/`:

#### Debit Cards
- `12_gazprom_debit.json`
- `13_loko_debit.json`
- `14_mts_debit.json`
- `16_raif_debit.json`

#### Credit Cards
- `17_gazprom_credit.json`
- `18_loko_credit.json`
- `19_mts_credit.json`
- `21_raif_credit.json`

#### Comparison Files (Updated)
- `1_debit_comparison.json` - Now includes all 8 banks
- `2_credit_comparison.json` - Now includes all 8 banks

## Bank Details

### Газпромбанк (Gazprombank)
- **Debit**: Золотая карта (Golden Card)
  - Annual fee: 0-490 ₽/year
  - Cashback: Up to 25% in categories
  - Interest on balance: Up to 4% annually
- **Credit**: Кредит 120 дней
  - Rate: 18%-40%
  - Grace period: 105 days
  - Limit: Up to 900,000 ₽

### Локобанк (Lokobank)
- **Debit**: Карта +Р
  - Free service
  - Cashback: Up to 25% in categories
  - Loyalty program with bonus points
- **Credit**: ТОП Кредит
  - Rate: 21%-45%
  - Grace period: 110 days
  - Limit: Up to 1,000,000 ₽

### МТС Банк (MTS Bank)
- **Debit**: Карта МТС
  - Annual fee: 0-1,470 ₽/year
  - Cashback: Up to 30% in categories
  - Interest on balance: Up to 6% annually
- **Credit**: Кредитная карта МТС
  - Rate: 24%-50%
  - Grace period: 115 days
  - Limit: Up to 1,100,000 ₽

### Райффайзенбанк (Raiffeisenbank)
- **Debit**: Фокус Карта
  - Free service
  - Cashback: Up to 40% in categories
  - Interest on balance: Up to 8% annually
- **Credit**: Кредитная карта Райффайзена
  - Rate: 30%-60%
  - Grace period: 125 days
  - Limit: Up to 1,300,000 ₽

## Usage

### Comparing Products

1. Navigate to **Срочный отчет (Urgent Report)** mode
2. Select any of the new banks from the dropdown
3. Choose product type (credit/debit card, deposit, loan)
4. Click **Анализировать** to generate comparison

### Analyzing Trends

1. Navigate to **Анализ трендов (Trends)** mode
2. Select any of the new banks
3. Choose product type and time period
4. View historical changes and trends

## Testing

To verify the integration:

```bash
# Start the application
python run.py

# Or with streamlit directly
streamlit run app/main.py
```

Test scenarios:
1. Select "Газпромбанк" + "Debit Card" → Should load comparison
2. Select "Локобанк" + "Credit Card" → Should load comparison
3. Select "МТС Банк" in Trends mode → Should analyze trends
4. Select "Райффайзенбанк" + any product → Should work correctly

## Future Improvements

- [ ] Add more product types for new banks (consumer loans, mortgages)
- [ ] Enhance scraper configurations with more detailed selectors
- [ ] Add historical data for trend analysis
- [ ] Include foreign banks (e.g., Plaza Mexico mentioned in user notes)
- [ ] Automated data updates from bank websites

## Notes

- All bank data files follow the same JSON schema structure
- Comparison files aggregate data from individual bank files
- LLM-powered comparison supports all new banks automatically
- Legacy comparison mode may need normalizer updates for full support

---

**Branch**: `feature/add-new-banks`  
**Date**: November 2025  
**Author**: McLovin (@twirlz-git)
