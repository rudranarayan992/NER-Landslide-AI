from __future__ import annotations

import argparse
import csv
from pathlib import Path

from scripts.ingestion.gsi_pipeline import GSI_EXTRACTED_DIR, normalize_records


def main() -> None:
    parser = argparse.ArgumentParser(description="Normalize raw GSI extraction rows and retain the original values as provenance.")
    parser.add_argument("--csv", type=str, default=None, help="Path to the raw extraction CSV. Defaults to the extracted GSI raw CSV.")
    args = parser.parse_args()

    raw_csv = Path(args.csv) if args.csv else next((GSI_EXTRACTED_DIR / p for p in GSI_EXTRACTED_DIR.glob("*_raw_extraction.csv")), None)
    if raw_csv is None or not raw_csv.exists():
        raise FileNotFoundError("No raw GSI extraction CSV found. Run extract_gsi_pdf.py first.")

    normalized_rows = normalize_records(raw_csv)
    print(f"Normalized {len(normalized_rows)} rows from {raw_csv.name}.")


if __name__ == "__main__":
    main()
