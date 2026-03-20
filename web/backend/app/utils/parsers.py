"""Utility parsers: target columns, translation rules."""

import json
import re
from typing import Dict, List


def parse_target_columns(raw: str) -> List[str]:
    """Parse target columns from JSON string or comma-separated text."""
    raw = raw.strip()
    if not raw:
        return []
    # Try JSON array first
    if raw.startswith("["):
        try:
            data = json.loads(raw)
            if isinstance(data, list):
                return [str(item).strip() for item in data if str(item).strip()]
        except json.JSONDecodeError:
            pass
    # Comma-separated (both EN and CN commas)
    items = re.split(r"[,，]", raw)
    return [item.strip() for item in items if item.strip()]


def parse_translation_rules(raw: str) -> Dict[str, str]:
    """Parse translation rules from JSON dict string or key=value lines."""
    raw = raw.strip()
    if not raw:
        return {}
    # Try JSON dict first
    if raw.startswith("{"):
        try:
            data = json.loads(raw)
            if isinstance(data, dict):
                return {str(k).strip(): str(v).strip() for k, v in data.items() if str(k).strip() and str(v).strip()}
        except json.JSONDecodeError:
            pass
    # key=value per line
    rules: Dict[str, str] = {}
    for line in raw.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        m = re.match(r"^(.+?)\s*=\s*(.+)$", line)
        if m:
            key = m.group(1).strip()
            val = m.group(2).strip()
            if key and val:
                rules[key] = val
    return rules


def validate_translation_rules_text(raw: str) -> list[str]:
    """Validate translation rules text, return list of error messages."""
    errors = []
    if not raw.strip():
        return errors
    # If not JSON, check key=value format
    if not raw.strip().startswith("{"):
        for i, line in enumerate(raw.strip().splitlines(), 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                errors.append(f"Line {i}: missing '=', expected format 'key=value'")
            elif not line.split("=", 1)[0].strip():
                errors.append(f"Line {i}: empty key")
            elif not line.split("=", 1)[1].strip():
                errors.append(f"Line {i}: empty value")
    return errors
