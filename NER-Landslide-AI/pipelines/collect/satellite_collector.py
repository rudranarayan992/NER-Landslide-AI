from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

from ner_landslide_ai.config import get_settings
from ner_landslide_ai.data_sources import make_metadata_for_source
from ner_landslide_ai.logging import get_logger
from ner_landslide_ai.validation import validate_metadata

logger = get_logger(__name__)
settings = get_settings()


def collect_satellite_data(source_url: Optional[str] = None, output_dir: Optional[str] = None) -> Dict[str, Any]:
    output_root = Path(output_dir or settings.raw_data_dir / "satellite")
    output_root.mkdir(parents=True, exist_ok=True)

    if not source_url:
        logger.warning("No satellite source configured; collector is idle until a valid source is supplied.")
        return {"status": "idle", "records": [], "metadata": []}

    metadata = make_metadata_for_source(
        source="satellite",
        source_url=source_url,
        provider="configured_source",
        dataset_name="satellite_data",
        geographic_coverage="NER India",
        raw_path=output_root / "satellite_raw",
    )

    validation = validate_metadata(metadata.to_dict())
    if not validation.valid:
        logger.error("Satellite metadata validation failed: %s", validation.issues)
        return {"status": "failed", "records": [], "metadata": [metadata.to_dict()]}

    logger.info("Satellite collector ready for real source ingestion: %s", source_url)
    return {"status": "ready", "records": [], "metadata": [metadata.to_dict()]}
