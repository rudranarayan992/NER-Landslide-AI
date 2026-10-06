from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class ValidationIssue:
    code: str
    message: str
    severity: str = "error"
    field: Optional[str] = None


@dataclass
class ValidationResult:
    valid: bool
    issues: List[ValidationIssue] = field(default_factory=list)
    file_path: Optional[str] = None

    def add_issue(self, code: str, message: str, severity: str = "error", field: Optional[str] = None) -> None:
        self.issues.append(ValidationIssue(code=code, message=message, severity=severity, field=field))
        if severity == "error":
            self.valid = False


def validate_file_exists(file_path: str | Path) -> ValidationResult:
    result = ValidationResult(valid=True, file_path=str(file_path))
    path = Path(file_path)
    if not path.exists():
        result.add_issue("missing_file", f"File not found: {file_path}", "error", "path")
    return result


def validate_metadata(metadata: Dict[str, Any]) -> ValidationResult:
    result = ValidationResult(valid=True)
    required_fields = [
        "source",
        "source_url",
        "download_timestamp",
        "dataset_name",
        "geographic_coverage",
    ]
    for field_name in required_fields:
        if field_name not in metadata or metadata[field_name] in (None, ""):
            result.add_issue("missing_metadata", f"Missing required metadata field: {field_name}", "error", field_name)
    return result


def validate_dataset_record(record: Dict[str, Any], required_fields: List[str]) -> ValidationResult:
    result = ValidationResult(valid=True)
    for field_name in required_fields:
        if field_name not in record or record[field_name] in (None, ""):
            result.add_issue("missing_record_field", f"Required record field missing: {field_name}", "error", field_name)
    return result
