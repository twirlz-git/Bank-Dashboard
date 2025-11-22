# Refactoring Guide: Unified Schema System

## Overview

This refactoring addresses **Issue #1: Hardcoded Comparison Data Issues** by implementing a unified schema system with flexible field mappings.

## Problem Statement

### Before Refactoring

The codebase had **inconsistent field names** across different data sources:

**Individual Bank Files** (`5_sberbank_debit.json`):
```json
{
  "стоимость": "Бесплатно",
  "снятие_наличных": {...},
  "переводы": {...}
}
```

**Comparison Files** (`1_debit_comparison.json`):
```json
{
  "стоимость_обслуживания": "Бесплатно",
  "снятие_наличных_чужие_банки": "1%",
  "переводы_по_реквизитам": "0%"
}
```

**Impact**:
- ❌ Comparator couldn't find matching fields
- ❌ Key mismatches during normalization
- ❌ Silent failures when fields were missing
- ❌ No validation of data quality

## Solution Architecture

### New Components

#### 1. **Field Mappings** (`configs/field_mappings.py`)

Centralized mapping of all possible field names to normalized internal names:

```python
CREDIT_CARD_FIELD_MAPPING = {
    # Individual file fields
    "стоимость": "annual_fee",
    "лимит": "max_limit",
    
    # Comparison file fields (different naming)
    "стоимость_обслуживания": "annual_fee",
    "кредитный_лимит": "max_limit",
}
```

**Features**:
- ✅ Maps all source field variations to unified names
- ✅ Handles nested structures (e.g., `снятие_наличных`)
- ✅ Supports field aliases
- ✅ Product-type specific mappings

#### 2. **Data Validator** (`modules/validator.py`)

Comprehensive validation system:

```python
validator = DataValidator()
is_valid, issues = validator.validate_product_data(data, "credit_card", "Sber")
completeness = validator.get_data_completeness_score(data, "credit_card")
```

**Capabilities**:
- ✅ Schema validation against expected fields
- ✅ Format validation (rates, amounts, dates)
- ✅ Data completeness scoring (0.0 to 1.0)
- ✅ Cross-file consistency checking
- ✅ Data freshness warnings
- ✅ Detailed issue reporting

#### 3. **Enhanced Normalizer** (`modules/normalizer.py`)

Refactored to use field mappings:

```python
class DataNormalizer:
    def _get_field_value(self, data: Dict, field_aliases: list):
        """Try multiple possible field names"""
        for alias in field_aliases:
            if alias in data:
                return data[alias]
        return None
```

**Improvements**:
- ✅ Tries multiple field name variations
- ✅ Handles both individual and comparison file formats
- ✅ Better error handling and logging
- ✅ Graceful degradation for missing fields

## Migration Guide

### For Existing Code

#### Before:
```python
# Direct field access - fragile
rate = card_data.get("ставка")
fee = card_data.get("стоимость")  # Might miss "стоимость_обслуживания"
```

#### After:
```python
# Use normalizer - robust
normalizer = DataNormalizer()
normalized = normalizer.normalize_credit_card(card_data, "Sber")
rate = normalized["interest_rate"]  # Always present
fee = normalized["annual_fee"]      # Always present
```

### Adding New Banks

#### 1. Add bank data file:
```json
// configs/bank_data/11_newbank_credit.json
{
  "банк": "NewBank",
  "карты": [...]
}
```

#### 2. Update scraper mapping:
```python
# modules/scraper.py
self.file_mapping = {
    "credit_card": {
        "NewBank": "11_newbank_credit.json",
        ...
    }
}
```

#### 3. Validate data:
```python
from modules.validator import DataValidator

validator = DataValidator()
is_valid, issues = validator.validate_product_data(
    newbank_data, "credit_card", "NewBank"
)

if not is_valid:
    print(f"Issues found: {issues}")
```

### Adding New Fields

#### 1. Update field mappings:
```python
# configs/field_mappings.py
CREDIT_CARD_FIELD_MAPPING = {
    "новое_поле": "new_field",
    ...
}
```

#### 2. Update schema:
```python
# configs/schemas.py
CREDIT_CARD_SCHEMA = {
    "fields": [..., "new_field"],
    "display_names": {
        "new_field": "Новое поле"
    }
}
```

#### 3. Add extraction method:
```python
# modules/normalizer.py
def _get_new_field(self, data: Dict[str, Any]) -> str:
    value = self._get_field_value(data, ["новое_поле", "new_field"])
    return self._format_value(value)
```

## Testing

### Validation Testing

```python
from modules.validator import DataValidator

validator = DataValidator()

# Test individual bank data
for bank in ["Sber", "VTB", "Alfa", "Tinkoff"]:
    data = scraper.get_product_data(bank, "credit_card")
    is_valid, issues = validator.validate_product_data(data, "credit_card", bank)
    
    if not is_valid:
        print(f"{bank} issues:")
        for issue in issues:
            print(f"  - {issue}")

# Test comparison file
comparison = load_json_config("configs/bank_data/2_credit_comparison.json")
is_valid, issues = validator.validate_comparison_data(comparison, "credit_card")
```

### Completeness Testing

```python
for bank in banks:
    data = scraper.get_product_data(bank, "credit_card")
    score = validator.get_data_completeness_score(data, "credit_card")
    print(f"{bank}: {score*100:.1f}% complete")
```

### Expected Output:
```
Sber: 95.5% complete
VTB: 90.9% complete  
Alfa: 81.8% complete ⚠️ Missing: min_salary_requirement
Tinkoff: 95.5% complete
```

## Benefits

### 1. **Robustness**
- ✅ Handles field name variations automatically
- ✅ No silent failures - validation catches issues
- ✅ Graceful degradation for missing data

### 2. **Maintainability**
- ✅ Single source of truth for field mappings
- ✅ Easy to add new banks/fields
- ✅ Self-documenting through mappings

### 3. **Quality**
- ✅ Data completeness scoring
- ✅ Format validation
- ✅ Freshness checking
- ✅ Detailed error reporting

### 4. **Flexibility**
- ✅ Supports multiple data source formats
- ✅ Easy to extend for new product types
- ✅ Configuration-driven approach

## Integration with Existing Code

The refactored components are **backward compatible**. The normalizer interface remains the same:

```python
# This still works!
normalizer = DataNormalizer()
result = normalizer.normalize_credit_card(data, "Sber")
```

But now it:
- ✅ Handles comparison file formats
- ✅ Tries multiple field name variations
- ✅ Provides better error messages
- ✅ Logs missing fields for debugging

## Next Steps

### Recommended Implementation Order:

1. ✅ **Field mappings** - Foundation for everything else
2. ✅ **Validator module** - Catch data issues early
3. ✅ **Enhanced normalizer** - Use mappings for normalization
4. ⏳ **Update main.py** - Add validation before processing
5. ⏳ **Add validation UI** - Show data quality to users
6. ⏳ **Create tests** - Validate all bank data files

### Future Enhancements:

- **Pydantic models** for type-safe validation
- **Auto-discovery** of bank files (no hardcoded mapping)
- **Data quality dashboard** showing completeness per bank
- **Automated data freshness checks** with notifications
- **Field mapping UI** for non-technical users

## Questions?

For issues or questions about the refactoring, refer to:
- `configs/field_mappings.py` - All field name variations
- `modules/validator.py` - Validation logic
- `modules/normalizer.py` - Normalization with mappings

---

**Status**: ✅ Core refactoring complete
**Branch**: `refactor/unified-schema`
**Next**: Integrate with main.py and add validation UI
