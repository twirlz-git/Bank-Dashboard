# Changelog - feature/backup_visual

## [Unreleased] - 2025-11-23

### ✨ Added

#### 1. PDF Export Support
- ✅ **PDF generation** for Urgent Mode (comparison reports)
- ✅ **PDF generation** for Trends Mode (trend analysis reports)
- 🎨 Beautiful formatting with tables, charts, and styled text
- 📄 Markdown support (bold, italic) converted to PDF-compatible format
- 📊 Charts embedded as images in PDF reports
- ⚠️ Auto-detection of `reportlab` availability with UI warnings

**Modified files:**
- `modules/report_generator.py`:
  - Added `generate_pdf_comparison()` method
  - Added `generate_pdf_trends()` method  
  - Added `_clean_markdown_for_pdf()` helper
  - Enhanced `get_filename()` to support PDF format parameter

#### 2. Full Debit Card Support
- 💳 **Debit cards** now fully supported alongside credit cards
- 📊 Specific fields for debit cards:
  - Interest on balance (процент на остаток)
  - SMS notifications cost
  - Withdrawals (own bank / other banks)
  - Transfers (SBP / by requisites)
  - Loyalty programs
- ✅ 8+ banks supported with debit card data

**Modified files:**
- `modules/normalizer.py`:
  - Added `normalize_debit_card()` method
  - Added `_get_withdrawals()` helper for withdrawal info extraction
  - Added `_get_transfers()` helper for transfer info extraction
- `app/main.py`:
  - Added "debit_card" option to product type selectors (both Urgent and Trends modes)
  - Integrated `normalize_debit_card()` into processing pipeline

#### 3. Confidence Indicators
- 🎯 **Confidence scoring** visible throughout the UI
- **Sidebar indicators:**
  - LLM status (✅ active / ⚠️ unavailable)
  - LLM model name display
  - Confidence level indication (90%+ high / 70% basic)
  - PDF export availability status
- **Urgent Mode indicators:**
  - Overall confidence metric (90% / 70%) with color-coded delta
  - Green: High (85%+)
  - Yellow: Medium (70-84%)
  - Red: Low (<70%)
- **Trends Mode indicators:**
  - Data source indicator (mock / real / web-search)
  - Overall confidence metric
  - Average confidence across timeline points
  - Individual point confidence in timeline table

**Modified files:**
- `app/main.py`:
  - Added confidence metrics display using `st.metric()`
  - Enhanced sidebar with status indicators
  - Color-coded confidence levels
  - Separate confidence tracking for Urgent and Trends modes
- `modules/trends_analyzer.py`:
  - Returns `confidence` score for each timeline point
  - Calculates `average_confidence` across all points
  - Added to summary data

#### 4. Dependencies
- ✅ Added `reportlab>=4.0.0` to `requirements.txt`

**Modified files:**
- `requirements.txt`: Added reportlab dependency

### 📝 Documentation
- ✅ Added `FEATURES_UPDATE.md` - comprehensive feature documentation
- ✅ Added `CHANGELOG_feature_backup_visual.md` - this file

**New files:**
- `FEATURES_UPDATE.md`
- `CHANGELOG_feature_backup_visual.md`

---

## 🛠️ Technical Details

### PDF Generation Implementation

**Libraries used:**
- `reportlab` - PDF generation
- `reportlab.platypus` - Document templates and flowables
- `reportlab.lib.styles` - Styling support

**Features:**
- Multi-page support with automatic page breaks
- Embedded chart images (saved temporarily, then deleted)
- Color-coded headers and sections
- Automatic table styling with alternating row colors
- Professional formatting matching XLSX reports

### Debit Card Normalization

**Field mapping strategy:**
- Reuses existing field extraction infrastructure
- Specific handlers for nested data (withdrawals, transfers)
- Fallback to "H/D" (Нет данных) for missing fields

**Supported banks:**
1. Сбербанк
2. ВТБ
3. Альфа-Банк
4. Т-Банк (Тинькофф)
5. Газпромбанк
6. Локобанк
7. МТС Банк
8. Райффайзенбанк

### Confidence Score Logic

**Urgent Mode:**
```python
if llm_enabled:
    confidence = 0.9  # 90% - LLM analysis
else:
    confidence = 0.7  # 70% - Basic comparison
```

**Trends Mode:**
```python
confidence = trends.get('confidence', 0.5)  # From analyzer
avg_point_confidence = mean([point['confidence'] for point in timeline])
```

**Data source mapping:**
- `mock` - Demo data (confidence ~0.75)
- `real_data_based` - From actual JSON files (confidence ~0.85)
- `web_search` - LLM-extracted from news (confidence variable)

---

## 🐛 Bug Fixes

None in this update (new features only).

---

## ⚠️ Breaking Changes

None. All changes are backward-compatible.

---

## 🚧 Known Limitations

1. **PDF Export:**
   - Requires `reportlab` package (optional dependency)
   - Charts require `kaleido` for image conversion
   - Large tables may span multiple pages

2. **Debit Cards:**
   - Data currently from local JSON files only
   - No real-time web scraping yet
   - Limited to 8 banks with pre-populated data

3. **Confidence Indicators:**
   - Fixed thresholds (not ML-based)
   - Urgent mode: binary (90% or 70%)
   - Trends mode: depends on data source quality

---

## 🚀 Future Improvements (Not in this PR)

- [ ] Real web scraping for debit card data
- [ ] ML-based confidence scoring
- [ ] Interactive PDF forms
- [ ] Batch comparison (multiple banks at once)
- [ ] Historical confidence tracking
- [ ] User-configurable confidence thresholds

---

## 💻 Installation & Usage

### Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run application
streamlit run app/main.py
```

### PDF Export Setup

```bash
# Install PDF support
pip install reportlab

# Verify in UI - sidebar should show:
# ✅ PDF экспорт доступен
```

### Using Debit Cards

1. Select **"Дебетовая карта"** from product type dropdown
2. Choose competitor bank
3. Click **"🔍 Анализировать"**
4. Review confidence indicator (🎯 metric in top-right)
5. Export to PDF or XLSX

---

## 📊 Commits in this Update

1. `8b8709f` - Add PDF export support to report generator
2. `9a84f51` - Add PDF export, debit cards support, and confidence indicators to UI
3. `f08caa4` - Add normalize_debit_card method for explicit debit card support
4. `ee3bcdd` - Add reportlab for PDF export support
5. `2023398` - Add documentation for new features
6. `[THIS]` - Add changelog for feature/backup_visual branch updates

---

## 👥 Contributors

This update developed by Sifer (@twirlz-git)

---

**Version:** MVP 2.1 (feature/backup_visual)  
**Date:** November 23, 2025  
**Status:** ✅ Ready for review
