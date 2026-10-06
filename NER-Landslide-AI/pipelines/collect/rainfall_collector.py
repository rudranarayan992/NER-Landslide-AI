from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

from ner_landslide_ai.config import get_settings
from ner_landslide_ai.data_sources import make_metadata_for_source
from ner_landslide_ai.logging import get_logger
from ner_landslide_ai.validation import validate_metadata

logger = get_logger(__name__)
settings = get_settings()


def collect_rainfall_data(source_url: Optional[str] = None, output_dir: Optional[str] = None) -> Dict[str, Any]:
    """Collect rainfall time series or gridded rainfall data when a valid source is configured."""
    output_root = Path(output_dir or settings.raw_data_dir / "rainfall")
    output_root.mkdir(parents=True, exist_ok=True)

    if not source_url:
        logger.warning("No rainfall source configured; collector is idle until a valid source is supplied.")
        return {"status": "idle", "records": [], "metadata": []}

    metadata = make_metadata_for_source(
        source="rainfall",
        source_url=source_url,
        provider="configured_source",
        dataset_name="rainfall_data",
        geographic_coverage="NER India",
        raw_path=output_root / "rainfall_raw",
    )

    validation = validate_metadata(metadata.to_dict())
    if not validation.valid:
        logger.error("Rainfall metadata validation failed: %s", validation.issues)
        return {"status": "failed", "records": [], "metadata": [metadata.to_dict()]}

    logger.info("Rainfall collector ready for real source ingestion: %s", source_url)
    return {"status": "ready", "records": [], "metadata": [metadata.to_dict()]}
