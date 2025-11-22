# Quick Start: Using Refactored Components

## Installation

```bash
# Clone the branch
git checkout refactor/unified-schema

# Install dependencies (no new dependencies added!)
pip install -r requirements.txt
```

## Running Tests

```bash
# Run validation test suite
python tests/test_refactoring.py
```

**Expected output:**
```
✅ Field mappings test PASSED
✅ Data validation test PASSED  
✅ Comparison validation test PASSED
✅ Normalization test PASSED
✅ Completeness scoring test PASSED

✅ ALL TESTS PASSED!
```

## Usage Examples

### 1. Validate Bank Data

```python
from modules.validator import DataValidator
from modules.utils import load_json_config

validator = DataValidator()

# Load bank data
data = load_json_config("configs/bank_data/6_sberbank_credit.json")
card = data["карты"][0]

# Validate
is_valid, issues = validator.validate_product_data(
    card, "credit_card", "Sber"
)

if not is_valid:
    print("Issues found:")
    for issue in issues:
        print(f"  - {issue}")

# Check completeness
score = validator.get_data_completeness_score(card, "credit_card")
print(f"Data completeness: {score*100:.1f}%")
```

### 2. Normalize Data from Any Source

```python
from modules.normalizer import DataNormalizer

normalizer = DataNormalizer()

# Works with individual files
individual_data = {"\u0441\u0442\u0430\u0432\u043a\u0430": "9.8%-49.8%", "\u043b\u0438\u043c\u0438\u0442": "\u0414\u043e 1 000 000 \u20bd"}
normalized1 = normalizer.normalize_credit_card(individual_data, "Sber")

# Also works with comparison files (different field names!)
comparison_data = {
    "\u0441\u0442\u0430\u0432\u043a\u0430": "17.9%-25.9%", 
    "\u043a\u0440\u0435\u0434\u0438\u0442\u043d\u044b\u0439_\u043b\u0438\u043c\u0438\u0442": "\u0414\u043e 600 000 \u20bd"
}
normalized2 = normalizer.normalize_credit_card(comparison_data, "VTB")

# Both produce consistent output:
print(normalized1["interest_rate"])  # "9.8%-49.8%"
print(normalized2["interest_rate"])  # "17.9%-25.9%"
print(normalized1["max_limit"])      # "До 1 000 000 ₽"
print(normalized2["max_limit"])      # "До 600 000 ₽"
```

### 3. Check Field Mappings

```python
from configs.field_mappings import (
    get_mapping_for_product,
    get_all_possible_field_names
)

# Get all mappings for credit cards
mapping = get_mapping_for_product("credit_card")
print(f"Credit cards have {len(mapping)} field mappings")

# Find all possible names for a field
aliases = get_all_possible_field_names("annual_fee")
print(f"'annual_fee' can be: {aliases}")
# ["стоимость", "стоимость_обслуживания", ...]
```

### 4. Generate Validation Report

```python
from modules.validator import DataValidator
from modules.utils import load_json_config

validator = DataValidator()

# Load comparison file
comparison = load_json_config("configs/bank_data/2_credit_comparison.json")
banks_data = comparison["банки"]

# Generate report
report = validator.generate_validation_report(banks_data, "credit_card")

print(f"Total banks: {report['total_banks']}")
print(f"Valid banks: {report['valid_banks']}")
print("\nCompleteness scores:")
for bank, score in report['completeness_scores'].items():
    print(f"  {bank}: {score}")
```

## Integration with Existing Code

**The refactoring is backward compatible!** Your existing code continues to work:

```python
# This still works exactly as before:
from modules.normalizer import DataNormalizer

normalizer = DataNormalizer()
result = normalizer.normalize_credit_card(card_data, "Sber")

# But now it:
# ✅ Handles comparison file formats
# ✅ Tries multiple field name variations  
# ✅ Logs missing fields for debugging
# ✅ Provides better error messages
```

## Adding New Banks

```python
# 1. Create data file
# configs/bank_data/12_newbank_credit.json

# 2. Update scraper (modules/scraper.py)
self.file_mapping = {
    "credit_card": {
        "NewBank": "12_newbank_credit.json",
        ...
    }
}

# 3. Validate it!
from modules.validator import DataValidator

validator = DataValidator()
data = load_json_config("configs/bank_data/12_newbank_credit.json")
card = data["карты"][0]

is_valid, issues = validator.validate_product_data(
    card, "credit_card", "NewBank"
)

if not is_valid:
    print("Fix these issues:")
    for issue in issues:
        print(f"  - {issue}")
```

## Key Files Reference

| File | Purpose | When to Use |
|------|---------|-------------|
| `configs/field_mappings.py` | Field name mappings | Adding new fields, checking aliases |
| `modules/validator.py` | Data validation | Checking data quality, finding issues |
| `modules/normalizer.py` | Data normalization | Converting to unified format |
| `configs/schemas.py` | Schema definitions | Adding new product types |
| `tests/test_refactoring.py` | Test suite | Validating changes |
| `docs/REFACTORING_GUIDE.md` | Full documentation | Detailed migration guide |

## Common Tasks

### Check if Sberbank data is valid
```bash
python -c "
from modules.validator import DataValidator
from modules.utils import load_json_config

validator = DataValidator()
data = load_json_config('configs/bank_data/6_sberbank_credit.json')
card = data['карты'][0]

is_valid, issues = validator.validate_product_data(card, 'credit_card', 'Sber')
print('✅ Valid' if is_valid else f'❌ Issues: {issues}')
"
```

### Get data completeness for all banks
```bash
python tests/test_refactoring.py
```

### Validate comparison files
```bash
python -c "
from modules.validator import DataValidator
from modules.utils import load_json_config

validator = DataValidator()
data = load_json_config('configs/bank_data/2_credit_comparison.json')

is_valid, issues = validator.validate_comparison_data(data, 'credit_card')
print('✅ Valid' if is_valid else f'⚠️ Issues found: {len(issues)}')
"
```

## Troubleshooting

### "Module not found" errors
```bash
# Make sure you're in the repo root
cd /path/to/Bank-Dashboard

# And using correct Python
python3 tests/test_refactoring.py
```

### "Field not found" warnings
This means your data uses a field name that's not in the mappings yet. Add it:

```python
# configs/field_mappings.py
CREDIT_CARD_FIELD_MAPPING = {
    "your_field_name": "normalized_name",
    ...
}
```

### Data validation fails
Run the validator to see specific issues:

```python
from modules.validator import DataValidator

validator = DataValidator()
is_valid, issues = validator.validate_product_data(
    your_data, "credit_card", "BankName"
)

for issue in issues:
    print(issue)  # Shows exactly what's wrong
```

## Next Steps

1. ✅ Run tests: `python tests/test_refactoring.py`
2. ✅ Review [REFACTORING_GUIDE.md](REFACTORING_GUIDE.md)
3. ✅ Check the [Pull Request](https://github.com/twirlz-git/Bank-Dashboard/pull/1)
4. ⏳ Merge to master
5. ⏳ Integrate validation into Streamlit UI

## Questions?

Refer to:
- [REFACTORING_GUIDE.md](REFACTORING_GUIDE.md) - Detailed documentation
- [Pull Request #1](https://github.com/twirlz-git/Bank-Dashboard/pull/1) - Implementation details
- `tests/test_refactoring.py` - Working examples
