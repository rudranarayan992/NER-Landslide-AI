from __future__ import annotations

from typing import Any, Mapping

from backend.app.config import NER_STATES


def is_valid_ner_state(value: str | None) -> bool:
    if value is None:
        return False
    return value.strip() in NER_STATES


def validate_ner_state(value: str | None, *, field_name: str = "state") -> tuple[bool, str | None]:
    if is_valid_ner_state(value):
        return True, None
    if value is None or not value.strip():
        return False, f"{field_name} is required and must be one of the NER states."
    return False, f"{field_name}='{value}' is outside the approved NER states: {', '.join(NER_STATES)}."


def validate_record_state(record: Mapping[str, Any], *, field_name: str = "state") -> tuple[bool, list[str]]:
    issues: list[str] = []
    if field_name not in record:
        issues.append(f"Missing required field: {field_name}.")
        return False, issues

    is_valid, message = validate_ner_state(str(record[field_name]), field_name=field_name)
    if not is_valid and message:
        issues.append(message)
    return is_valid, issues
