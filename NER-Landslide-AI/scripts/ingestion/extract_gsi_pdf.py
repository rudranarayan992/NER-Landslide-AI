from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from scripts.ingestion.gsi_pipeline import extract_pdf_text, find_gsi_pdf, inspect_pdf, VALIDATION_REPORT_PATH, GSI_EXTRACTED_DIR


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract text from the local GSI PDF page-by-page and save the raw output.")
    parser.add_argument("--pdf", type=str, default=None, help="Path to the source PDF. Defaults to the project GSI folder.")
    args = parser.parse_args()

    pdf_path = Path(args.pdf) if args.pdf else find_gsi_pdf()
    if pdf_path is None:
        raise FileNotFoundError("No local GSI PDF found under data/raw/landslides/.")

    summary = inspect_pdf(pdf_path, sample_pages=min(10, max(1, pdf_path.stat().st_size > 0 and 10)))
    print(json.dumps({"inspection": summary}, indent=2, ensure_ascii=False))

    extracted_rows = extract_pdf_text(pdf_path)
    print(json.dumps({"rows_extracted": len(extracted_rows), "output_dir": str(GSI_EXTRACTED_DIR)}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
