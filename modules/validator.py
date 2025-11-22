"""
modules/validator.py - Data validation and schema checking

Provides validation for bank data against expected schemas,
ensuring data quality and completeness.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from pathlib import Path

from configs.schemas import get_schema
from configs.field_mappings import (
    get_mapping_for_product,
    get_all_possible_field_names,
    NESTED_FIELD_HANDLERS
)

logger = logging.getLogger(__name__)


class DataValidator:
    """Validate bank product data against schemas"""

    def __init__(self):
        self.validation_results = []

    def validate_product_data(
        self, 
        data: Dict[str, Any], 
        product_type: str,
        bank: str = "Unknown"
    ) -> Tuple[bool, List[str]]:
        """
        Validate product data against schema.
        
        Returns:
            Tuple[bool, List[str]]: (is_valid, list_of_issues)
        """
        issues = []
        schema = get_schema(product_type)
        
        if not schema:
            issues.append(f"⚠️ Unknown product type: {product_type}")
            return False, issues
        
        # Check for required fields
        required_fields = schema.get("fields", [])
        mapping = get_mapping_for_product(product_type)
        
        for field in required_fields:
            if field == "bank":  # Bank is added during normalization
                continue
                
            # Check if field exists in data (considering aliases)
            field_found = self._check_field_exists(data, field, mapping)
            
            if not field_found:
                possible_names = get_all_possible_field_names(field)
                issues.append(
                    f"❌ Missing required field '{field}' for {bank}. "
                    f"Expected one of: {', '.join(possible_names[:3])}"
                )
        
        # Check data types and formats
        format_issues = self._validate_field_formats(data, product_type)
        issues.extend(format_issues)
        
        # Check for data freshness
        freshness_issue = self._check_data_freshness(data)
        if freshness_issue:
            issues.append(freshness_issue)
        
        is_valid = len(issues) == 0
        
        if not is_valid:
            logger.warning(f"Validation failed for {bank} - {product_type}: {len(issues)} issues found")
        
        return is_valid, issues

    def validate_comparison_data(
        self,
        comparison_data: Dict[str, Any],
        product_type: str
    ) -> Tuple[bool, List[str]]:
        """
        Validate comparison file data structure.
        
        Checks that all banks in comparison have consistent fields.
        """
        issues = []
        
        banks_data = comparison_data.get("банки", {})
        
        if not banks_data:
            issues.append("❌ Comparison file missing 'банки' section")
            return False, issues
        
        # Get all field names from all banks
        all_fields = set()
        bank_fields = {}
        
        for bank, bank_data in banks_data.items():
            fields = set(bank_data.keys())
            bank_fields[bank] = fields
            all_fields.update(fields)
        
        # Check for inconsistent fields across banks
        for bank, fields in bank_fields.items():
            missing = all_fields - fields
            if missing:
                issues.append(
                    f"⚠️ {bank} missing fields: {', '.join(list(missing)[:5])}"
                )
        
        # Validate each bank's data
        for bank, bank_data in banks_data.items():
            _, bank_issues = self.validate_product_data(bank_data, product_type, bank)
            issues.extend([f"{bank}: {issue}" for issue in bank_issues])
        
        is_valid = len(issues) == 0
        return is_valid, issues

    def get_data_completeness_score(
        self, 
        data: Dict[str, Any], 
        product_type: str
    ) -> float:
        """
        Calculate completeness score (0.0 to 1.0) for product data.
        
        Returns:
            float: Percentage of required fields present with valid data
        """
        schema = get_schema(product_type)
        required_fields = [f for f in schema.get("fields", []) if f != "bank"]
        mapping = get_mapping_for_product(product_type)
        
        if not required_fields:
            return 1.0
        
        fields_present = 0
        for field in required_fields:
            if self._check_field_exists(data, field, mapping):
                value = self._get_field_value(data, field, mapping)
                # Check if value is meaningful (not N/A, Н/Д, etc.)
                if value and value not in ["Н/Д", "N/A", "Н/Д", "", "None"]:
                    fields_present += 1
        
        return fields_present / len(required_fields)

    def _check_field_exists(
        self, 
        data: Dict[str, Any], 
        normalized_field: str,
        mapping: Dict[str, str]
    ) -> bool:
        """Check if a normalized field exists in data (checking all possible names)"""
        # Get all possible source field names
        possible_names = get_all_possible_field_names(normalized_field)
        
        # Also check the mapping
        for source, target in mapping.items():
            if target == normalized_field:
                possible_names.append(source)
        
        # Check if any of these names exist in data
        for name in possible_names:
            if name in data:
                return True
            
            # Check nested structures
            if name in NESTED_FIELD_HANDLERS:
                return True
        
        return False

    def _get_field_value(
        self,
        data: Dict[str, Any],
        normalized_field: str,
        mapping: Dict[str, str]
    ) -> Any:
        """Get field value from data using various possible field names"""
        possible_names = get_all_possible_field_names(normalized_field)
        
        for name in possible_names:
            if name in data:
                return data[name]
        
        return None

    def _validate_field_formats(self, data: Dict[str, Any], product_type: str) -> List[str]:
        """Validate that fields have expected formats"""
        issues = []
        
        # Check interest rate format
        for rate_field in ["ставка", "процент"]:
            if rate_field in data:
                rate = data[rate_field]
                if rate and rate not in ["Нет", "Н/Д"]:
                    if not isinstance(rate, (int, float)) and not self._is_valid_rate_string(rate):
                        issues.append(f"⚠️ Invalid rate format: '{rate}'")
        
        # Check amount fields
        for amount_field in ["лимит", "кредитный_лимит", "сумма"]:
            if amount_field in data:
                amount = data[amount_field]
                if amount and not self._is_valid_amount_string(str(amount)):
                    issues.append(f"⚠️ Invalid amount format: '{amount}'")
        
        return issues

    def _is_valid_rate_string(self, rate_str: str) -> bool:
        """Check if string represents a valid rate"""
        if not isinstance(rate_str, str):
            return False
        
        # Remove common characters
        cleaned = rate_str.replace('%', '').replace(' ', '').replace('₽', '')
        
        # Check for range format (e.g., "9.8-49.8")
        if '-' in cleaned:
            parts = cleaned.split('-')
            return all(self._is_number(p) for p in parts)
        
        # Check for "до X%" format
        if cleaned.startswith('до'):
            num_part = cleaned.replace('до', '').strip()
            return self._is_number(num_part)
        
        return self._is_number(cleaned)

    def _is_valid_amount_string(self, amount_str: str) -> bool:
        """Check if string represents a valid amount"""
        if 'Бесплатно' in amount_str or 'Н/Д' in amount_str:
            return True
        
        # Remove currency symbols and spaces
        cleaned = amount_str.replace('₽', '').replace(' ', '').replace(',', '')
        
        # Check for range
        if 'До' in cleaned or 'до' in cleaned.lower():
            return True
        
        return self._is_number(cleaned) or '-' in cleaned

    def _is_number(self, s: str) -> bool:
        """Check if string can be converted to number"""
        try:
            float(s.replace(',', '.'))
            return True
        except (ValueError, AttributeError):
            return False

    def _check_data_freshness(self, data: Dict[str, Any]) -> Optional[str]:
        """Check if data has a date field and warn if old"""
        date_field = data.get("дата")
        if not date_field:
            return "⚠️ No date field found in data"
        
        # Parse date (assuming format like "ноябрь 2025")
        try:
            current_date = datetime.now()
            # Simple check: if it's not the current year
            if str(current_date.year) not in str(date_field):
                return f"⚠️ Data may be outdated: {date_field}"
        except Exception as e:
            logger.debug(f"Could not parse date: {date_field}, {e}")
        
        return None

    def generate_validation_report(
        self,
        all_data: Dict[str, Dict[str, Any]],
        product_type: str
    ) -> Dict[str, Any]:
        """
        Generate comprehensive validation report for multiple banks.
        
        Args:
            all_data: Dict[bank_name, bank_data]
            product_type: Type of product
        
        Returns:
            Dict with validation summary and details
        """
        report = {
            "product_type": product_type,
            "total_banks": len(all_data),
            "valid_banks": 0,
            "banks_with_issues": [],
            "completeness_scores": {},
            "common_issues": [],
        }
        
        all_issues = []
        
        for bank, data in all_data.items():
            is_valid, issues = self.validate_product_data(data, product_type, bank)
            completeness = self.get_data_completeness_score(data, product_type)
            
            report["completeness_scores"][bank] = f"{completeness * 100:.1f}%"
            
            if is_valid:
                report["valid_banks"] += 1
            else:
                report["banks_with_issues"].append({
                    "bank": bank,
                    "issues": issues,
                    "completeness": f"{completeness * 100:.1f}%"
                })
                all_issues.extend(issues)
        
        # Find common issues
        issue_counts = {}
        for issue in all_issues:
            # Extract issue type (remove bank-specific details)
            issue_type = issue.split(":")[-1].strip()
            issue_counts[issue_type] = issue_counts.get(issue_type, 0) + 1
        
        # Get top 5 most common issues
        sorted_issues = sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)
        report["common_issues"] = [
            {"issue": issue, "count": count} 
            for issue, count in sorted_issues[:5]
        ]
        
        return report
