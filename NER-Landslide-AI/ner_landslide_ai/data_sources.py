from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


@dataclass
class DataSourceMetadata:
    """Core metadata required for every external source ingested into the project."""

    source: str
    source_url: str
    provider: Optional[str] = None
    download_timestamp: Optional[str] = None
    dataset_name: Optional[str] = None
    dataset_date: Optional[str] = None
    dataset_version: Optional[str] = None
    geographic_coverage: Optional[str] = None
    license: Optional[str] = None
    processing_step: str = "raw_ingestion"
    file_hash: Optional[str] = None
    raw_path: Optional[str] = None
    status: str = "pending"
    notes: Optional[str] = None
    extras: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        payload = {
            "source": self.source,
            "source_url": self.source_url,
            "provider": self.provider,
            "download_timestamp": self.download_timestamp or datetime.now(timezone.utc).isoformat(),
            "dataset_name": self.dataset_name,
            "dataset_date": self.dataset_date,
            "dataset_version": self.dataset_version,
            "geographic_coverage": self.geographic_coverage,
            "license": self.license,
            "processing_step": self.processing_step,
            "file_hash": self.file_hash,
            "raw_path": self.raw_path,
            "status": self.status,
            "notes": self.notes,
        }
        payload.update(self.extras)
        return payload


def make_metadata_for_source(
    *,
    source: str,
    source_url: str,
    provider: Optional[str] = None,
    dataset_name: Optional[str] = None,
    dataset_date: Optional[str] = None,
    geographic_coverage: str = "NER India",
    license: Optional[str] = None,
    raw_path: Optional[Path | str] = None,
    processing_step: str = "raw_ingestion",
    extras: Optional[Dict[str, Any]] = None,
) -> DataSourceMetadata:
    return DataSourceMetadata(
        source=source,
        source_url=source_url,
        provider=provider,
        dataset_name=dataset_name,
        dataset_date=dataset_date,
        geographic_coverage=geographic_coverage,
        license=license,
        raw_path=str(raw_path) if raw_path else None,
        processing_step=processing_step,
        extras=extras or {},
    )
