"""
modules/utils.py - Utility functions for data processing
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

def load_json_config(filepath: str) -> Dict[str, Any]:
    """Load JSON configuration file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"Config file not found: {filepath}")
        return {}
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in: {filepath}")
        return {}

def save_json_cache(data: Dict[str, Any], filename: str, cache_dir: str = "./cache"):
    """Save data to JSON cache file"""
    Path(cache_dir).mkdir(exist_ok=True)
    filepath = Path(cache_dir) / filename
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    logger.info(f"Cache saved: {filepath}")

def normalize_rate(rate_str: str) -> Optional[float]:
    """Convert rate string to float (handles % symbol)"""
    if not rate_str:
        return None
    try:
        return float(str(rate_str).replace('%', '').strip())
    except (ValueError, AttributeError):
        return None

def normalize_currency(value: str, currency: str = "RUB") -> Dict[str, Any]:
    """Parse currency value"""
    return {
        "value": value,
        "currency": currency
    }

def extract_number(text: str) -> Optional[float]:
    """Extract first number from text"""
    import re
    match = re.search(r'[\d,\.]+', str(text))
    if match:
        return float(match.group().replace(',', '.'))
    return None

def format_timestamp() -> str:
    """Get current timestamp as formatted string"""
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def get_field_display_name(field: str, schema_dict: Dict) -> str:
    """Get human-readable field name from schema"""
    display_names = schema_dict.get("display_names", {})
    return display_names.get(field, field)

def merge_data_safely(base: Dict, update: Dict) -> Dict:
    """Merge two dicts, preserving non-None values from base"""
    result = base.copy()
    for key, value in update.items():
        if value is not None:
            result[key] = value
    return result
