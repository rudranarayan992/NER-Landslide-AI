from __future__ import annotations

import argparse
import json
from pathlib import Path

from scripts.ingestion.gsi_pipeline import inspect_pdf, find_gsi_pdf, detect_text_based_document


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspect the local GSI PDF before extraction.")
    parser.add_argument("--pdf", type=str, default=None, help="Path to a local GSI PDF. Defaults to the project data/raw/landslides/gsi folder.")
    parser.add_argument("--sample-pages", type=int, default=10, help="Number of pages to inspect for text and table detection.")
    args = parser.parse_args()

    pdf_path = Path(args.pdf) if args.pdf else find_gsi_pdf()
    if pdf_path is None:
        raise FileNotFoundError("No local GSI PDF found under data/raw/landslides/.")

    summary = inspect_pdf(pdf_path, sample_pages=args.sample_pages)
    summary["is_text_based"] = detect_text_based_document(pdf_path)
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
