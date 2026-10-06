from __future__ import annotations

from pathlib import Path

from scripts.ingestion.gsi_pipeline import detect_text_based_document, find_gsi_pdf, normalize_date, normalize_whitespace


def test_find_gsi_pdf() -> None:
    pdf_path = find_gsi_pdf()
    assert pdf_path is not None
    assert pdf_path.suffix.lower() == ".pdf"


def test_normalize_helpers() -> None:
    assert normalize_whitespace("  Assam   district  ") == "Assam district"
    assert normalize_date("12/08/2022") == "2022-08-12"


def test_detect_text_based_document() -> None:
    pdf_path = find_gsi_pdf()
    assert isinstance(detect_text_based_document(pdf_path), bool)
