# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
- **Multi-Bank Comparison Feature** - Compare Sberbank against multiple competitors simultaneously
  - New mode in sidebar: "🔄 Мульти-банк сравнение"
  - Multiselect widget for choosing 1-7 competitor banks
  - Horizontal table layout: Sberbank first, then competitors (as columns)
  - Comparison criteria listed vertically (as rows)
  - LLM-powered intelligent parameter extraction and analysis
  - Key insights mentioning specific banks and metrics
  - Sberbank advantages section
  - Competitor highlights organized by bank
  - Overall recommendation considering full competitive landscape
  - Comprehensive documentation in `docs/MULTI_BANK_COMPARISON.md`

### Technical Changes
- New module: `modules/multi_bank_comparator.py`
  - `MultiBankComparator` class for multi-bank comparison logic
  - Integration with `LLMComparator` for intelligent analysis
  - Sophisticated LLM prompt for structured multi-bank output
  - Fallback to basic comparison when LLM unavailable
- Updated `app/main.py`:
  - Added third mode option in sidebar
  - New UI section with product selector and bank multiselect
  - Results display with comparison table and insights
  - Support for competitor highlights by bank

### Documentation
- Added `docs/MULTI_BANK_COMPARISON.md` with:
  - Feature overview and capabilities
  - Step-by-step usage guide
  - Technical architecture details
  - Example use cases
  - Troubleshooting guide
  - Future enhancement ideas

## [Previous Versions]

_Version history to be documented_
