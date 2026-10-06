from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

from ner_landslide_ai.config import get_settings
from ner_landslide_ai.data_sources import make_metadata_for_source
from ner_landslide_ai.logging import get_logger
from ner_landslide_ai.validation import validate_metadata

logger = get_logger(__name__)
settings = get_settings()


def collect_landslide_data(source_url: Optional[str] = None, output_dir: Optional[str] = None) -> Dict[str, Any]:
    """Collect historical landslide inventory data only when a valid source is configured."""
    output_root = Path(output_dir or settings.raw_data_dir / "landslides")
    output_root.mkdir(parents=True, exist_ok=True)

    if not source_url:
        logger.warning("No landslide inventory source configured; collector is idle until a valid source is supplied.")
        return {"status": "idle", "records": [], "metadata": []}

    metadata = make_metadata_for_source(
        source="historical_landslide_inventory",
        source_url=source_url,
        provider="configured_source",
        dataset_name="historical_landslide_inventory",
        geographic_coverage="NER India",
        raw_path=output_root / "historical_landslide_inventory_raw",
    )

    validation = validate_metadata(metadata.to_dict())
    if not validation.valid:
        logger.error("Landslide metadata validation failed: %s", validation.issues)
        return {"status": "failed", "records": [], "metadata": [metadata.to_dict()]}

    logger.info("Landslide collector ready for real source ingestion: %s", source_url)
    return {"status": "ready", "records": [], "metadata": [metadata.to_dict()]}
