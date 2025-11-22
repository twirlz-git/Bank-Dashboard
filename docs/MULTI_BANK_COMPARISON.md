# Multi-Bank Comparison Feature

## Overview

The Multi-Bank Comparison feature allows you to compare **Sberbank's products against multiple competitors simultaneously** in a single view. This feature presents comparison data in a table format with Sberbank listed first (horizontally), followed by competitor banks, with comparison criteria listed vertically.

## Key Features

### 1. **Multiple Bank Selection**
- Select from 1 to 7 competitor banks for comparison
- Available banks:
  - VTB (ВТБ)
  - Alfa Bank (Альфа)
  - Tinkoff (Тинькофф)
  - Gazprombank (Газпромбанк)
  - Loko Bank (Локобанк)
  - MTS Bank (МТС Банк)
  - Raiffeisenbank (Райффайзенбанк)

### 2. **Product Types Supported**
- Credit Cards (Кредитная карта)
- Debit Cards (Дебетовая карта)
- Deposits (Вклад)
- Consumer Loans (Потребительский кредит)

### 3. **LLM-Powered Intelligent Comparison**
- Uses AI to dynamically extract and compare all relevant parameters
- Adapts to available data without hardcoded field mappings
- Generates contextual insights and recommendations
- Identifies best values for each parameter across all banks

### 4. **Comparison Table Format**

**Horizontal Layout:**
```
Параметр       | Сбербанк | ВТБ   | Альфа | Тинькофф
----------------|-------------|-------|--------|-------------
Проц. ставка | 17.9%       | 18.5% | 16.9%  | 19.9%
Стоимость   | 0₽         | 0₽   | 490₽  | 0₽
...
```

- **First Column**: Parameter names (criteria)
- **Second Column**: Sberbank values (reference point)
- **Remaining Columns**: Competitor values

### 5. **Comprehensive Analysis Output**

#### Key Insights
- 4-6 data-driven insights highlighting important findings
- Uses ✓ for positive findings and ⚠️ for warnings
- Mentions specific banks and concrete numbers
- Formatted with Markdown for better readability

#### Sberbank Advantages
- List of areas where Sberbank outperforms competitors
- Specific metrics and values highlighted

#### Competitor Highlights
- Individual strong points for each competitor bank
- Organized by bank for easy comparison
- Helps identify which competitor excels in which area

#### Overall Recommendation
- 2-3 sentence summary based on the comparison
- Actionable insights for decision-making

## How to Use

### Step 1: Access Multi-Bank Comparison Mode
1. Open the Bank Dashboard application
2. In the sidebar, select **"🔄 Мульти-банк сравнение"**

### Step 2: Select Product Type
- Choose the type of product you want to compare from the dropdown

### Step 3: Select Competitor Banks
- Use the multi-select widget to choose banks for comparison
- You can select anywhere from 1 to 7 banks
- Default selection: VTB and Alfa Bank

### Step 4: Run Comparison
- Click the **"🔍 Сравнить с конкурентами"** button
- Wait for data collection and analysis (LLM-powered)

### Step 5: Review Results
- **Comparison Table**: See all parameters side-by-side
- **Key Insights**: Read important findings
- **Sber Advantages**: Understand where Sberbank leads
- **Competitor Highlights**: See what each competitor does best
- **Recommendation**: Get an overall assessment

## Technical Architecture

### New Module: `multi_bank_comparator.py`

**Location**: `modules/multi_bank_comparator.py`

**Key Components:**

#### `MultiBankComparator` Class
- Main class handling multi-bank comparison logic
- Integrates with `LLMComparator` for intelligent analysis

#### Methods:

##### `compare_multiple_banks()`
```python
def compare_multiple_banks(
    sber_data: Dict[str, Any],
    competitor_data_list: List[Dict[str, Any]],
    bank_names: List[str],
    product_type: str
) -> Dict[str, Any]
```
Main entry point for multi-bank comparison.

##### `_llm_multi_comparison()`
Uses LLM to intelligently extract and structure comparison data for multiple banks.

##### `_create_multi_bank_table()`
Creates pandas DataFrame with Sberbank as first column, followed by competitors.

##### `_generate_multi_bank_insights()`
Generates contextual insights mentioning specific banks and metrics.

##### `_basic_multi_comparison()`
Fallback method when LLM is unavailable.

### LLM Prompt Structure

The multi-bank comparison uses a sophisticated prompt that:
1. Provides all bank data (Sberbank + all competitors) to the LLM
2. Requests structured JSON output with:
   - Parameters with values for each bank
   - Best bank for each parameter
   - Sberbank advantages
   - Competitor highlights (organized by bank)
   - Overall recommendation

### Integration with Main App

**Updated**: `app/main.py`

**Changes:**
1. Added import for `MultiBankComparator`
2. Initialized multi_comparator in session state
3. Added new radio button option: "🔄 Мульти-банк сравнение"
4. Created new UI section with:
   - Product type selector
   - Multi-select for banks
   - Analysis button
   - Results display area

## Requirements

### Dependencies
- All existing dependencies from `requirements.txt`
- LLM API access (OpenRouter or OpenAI)
- API key configured in environment

### Data Requirements
- Bank product data must be available in the expected format
- Each bank needs to have data files for the selected product type

## Advantages Over Single-Bank Comparison

1. **Time Efficiency**: Compare multiple competitors in one analysis instead of running separate comparisons
2. **Holistic View**: See the full competitive landscape at once
3. **Better Context**: Understand relative positioning across all competitors
4. **Parameter-Centric**: Focus on criteria rather than individual bank-to-bank comparisons
5. **Actionable Insights**: Get recommendations considering all competitive options

## Limitations

1. **Data Availability**: All selected banks must have data available for the chosen product type
2. **LLM Dependency**: Best results require LLM access; fallback mode provides basic comparison only
3. **Column Width**: Too many banks (>5) may make the table harder to read on smaller screens
4. **Export**: XLSX export for multi-bank comparisons is not yet implemented

## Future Enhancements

1. **Export Functionality**: Add XLSX export for multi-bank comparison results
2. **Visual Highlights**: Color-code cells to show best/worst values
3. **Filtering**: Allow filtering parameters by category
4. **Ranking**: Add overall ranking of banks by number of "best" parameters
5. **Historical Comparison**: Compare how multiple banks have changed over time
6. **Custom Parameter Weights**: Let users specify which parameters matter most

## Example Use Cases

### Use Case 1: Competitive Analysis
**Scenario**: Product manager wants to understand Sberbank's credit card positioning

**Steps:**
1. Select Credit Card product type
2. Select all 7 competitor banks
3. Run comparison
4. Review where Sberbank leads and lags
5. Use insights for product strategy decisions

### Use Case 2: Urgent Response
**Scenario**: Competitor launches aggressive deposit promotion

**Steps:**
1. Select Deposit product type
2. Select the specific competitor + 2-3 others
3. Run comparison
4. Quickly see if adjustment is needed
5. Use recommendation for executive decision

### Use Case 3: Market Research
**Scenario**: Understanding debit card market landscape

**Steps:**
1. Select Debit Card product type
2. Select top 5 competitors
3. Run comparison
4. Identify market trends and gaps
5. Export for presentation (coming soon)

## Troubleshooting

### Issue: "No data available for [Bank]"
**Solution**: Check that the bank has data files for the selected product type in the data directory.

### Issue: "LLM unavailable - basic comparison"
**Solution**: 
1. Check that your API key is configured in the environment
2. Verify API key has sufficient credits
3. Check internet connection

### Issue: Table is too wide
**Solution**: 
1. Reduce number of selected banks
2. Use full-screen mode
3. Export to XLSX (when available) for better viewing

## Support

For issues or questions about the multi-bank comparison feature:
1. Check existing documentation
2. Review the code in `modules/multi_bank_comparator.py`
3. Open an issue on GitHub with detailed description

---

**Version**: 1.0  
**Last Updated**: November 2025  
**Author**: Bank Dashboard Team
