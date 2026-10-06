from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from ner_landslide_ai.validation import ValidationResult, validate_file_exists


class DatasetValidator:
    """Thin validation framework to be extended with source-specific rules."""

    def __init__(self, accepted_extensions: Optional[Iterable[str]] = None):
        self.accepted_extensions = set(accepted_extensions or {".csv", ".geojson", ".gpkg", ".shp", ".json", ".tif", ".tiff", ".zip"})

    def validate_file(self, file_path: str | Path) -> ValidationResult:
        result = validate_file_exists(file_path)
        if not result.valid:
            return result

        path = Path(file_path)
        if path.suffix.lower() not in self.accepted_extensions:
            result.add_issue("unsupported_extension", f"Unsupported dataset extension for file: {path.name}", "warning", "extension")
        return result

    def validate_directory(self, directory_path: str | Path) -> Dict[str, Any]:
        directory = Path(directory_path)
        files = list(directory.rglob("*")) if directory.exists() else []
        file_results = [self.validate_file(path) for path in files if path.is_file()]
        valid_count = sum(1 for item in file_results if item.valid)
        issue_count = sum(len(item.issues) for item in file_results)
        return {
            "path": str(directory),
            "exists": directory.exists(),
            "file_count": len(files),
            "valid_files": valid_count,
            "issue_count": issue_count,
            "results": [result.__dict__ for result in file_results],
        }
