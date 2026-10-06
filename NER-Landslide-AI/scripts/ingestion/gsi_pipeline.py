from __future__ import annotations

import csv
import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import fitz

from ner_landslide_ai.config import NER_STATES
from ner_landslide_ai.logging import get_logger

LOGGER = get_logger("gsi_pipeline")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_GSI_DIR = PROJECT_ROOT / "data" / "raw" / "landslides" / "gsi"
PROCESSED_LANDSLIDES_DIR = PROJECT_ROOT / "data" / "processed" / "landslides"
RAW_TEXT_DIR = PROCESSED_LANDSLIDES_DIR / "gsi_raw_text"
GSI_TABLES_DIR = PROCESSED_LANDSLIDES_DIR / "gsi_tables"
GSI_EXTRACTED_DIR = PROCESSED_LANDSLIDES_DIR / "gsi_extracted"
VALIDATION_REPORT_PATH = PROCESSED_LANDSLIDES_DIR / "gsi_validation_report.json"

STATE_PATTERN = re.compile("|".join(re.escape(state) for state in NER_STATES), flags=re.IGNORECASE)


def ensure_directories() -> None:
    for directory in (RAW_GSI_DIR, PROCESSED_LANDSLIDES_DIR, RAW_TEXT_DIR, GSI_TABLES_DIR, GSI_EXTRACTED_DIR):
        directory.mkdir(parents=True, exist_ok=True)


def find_gsi_pdf() -> Path | None:
    ensure_directories()
    candidate_roots = [RAW_GSI_DIR, PROJECT_ROOT / "data" / "raw" / "landslides"]
    for root in candidate_roots:
        if not root.exists():
            continue
        pdf_candidates = sorted(root.rglob("*.pdf"))
        if pdf_candidates:
            return pdf_candidates[0]
    return None


def normalize_whitespace(value: str | None) -> str:
    if value is None:
        return ""
    return re.sub(r"\s+", " ", value).strip()


def normalize_date(value: str | None) -> str:
    if value is None:
        return ""
    cleaned = normalize_whitespace(value)
    if not cleaned:
        return ""
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%m/%d/%Y", "%d.%m.%Y", "%d %b %Y", "%d %B %Y"):
        try:
            parsed = datetime.strptime(cleaned, fmt)
            return parsed.date().isoformat()
        except ValueError:
            continue
    return cleaned


def parse_float(value: str | None) -> float | None:
    if value is None:
        return None
    cleaned = normalize_whitespace(value).replace(",", "")
    if not cleaned:
        return None
    match = re.search(r"-?\d+(?:\.\d+)?", cleaned)
    if not match:
        return None
    try:
        return float(match.group(0))
    except ValueError:
        return None


def detect_state_in_text(text: str) -> str:
    if not text:
        return ""
    matches = [state for state in NER_STATES if re.search(re.escape(state), text, flags=re.IGNORECASE)]
    if matches:
        return matches[0]
    return ""


def extract_district_hint(text: str) -> str:
    pattern = re.compile(r"(?:district|distr\.?|sub-?district)\s*[:\-]?\s*([A-Za-z][A-Za-z .'-]{1,80})", flags=re.IGNORECASE)
    match = pattern.search(text)
    if match:
        return normalize_whitespace(match.group(1))
    return ""


def extract_location_hint(text: str) -> str:
    patterns = [
        r"(?:location|village|near|at)\s*[:\-]?\s*([A-Za-z0-9][A-Za-z0-9 .',/-]{1,120})",
        r"(?:area|site)\s*[:\-]?\s*([A-Za-z0-9][A-Za-z0-9 .',/-]{1,120})",
    ]
    for pattern_text in patterns:
        match = re.search(pattern_text, text, flags=re.IGNORECASE)
        if match:
            return normalize_whitespace(match.group(1))
    return ""


def extract_date_hint(text: str) -> str:
    patterns = [
        r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",
        r"\b\d{4}-\d{2}-\d{2}\b",
        r"\b\d{1,2}\s+[A-Za-z]{3,9}\s+\d{2,4}\b",
        r"\b\d{1,2}\s+[A-Za-z]+\s+\d{2,4}\b",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return normalize_date(match.group(0))
    return ""


def extract_latitude(text: str) -> str:
    patterns = [
        r"(?i)\b(\d{1,3}(?:\.\d+)?)\s*(?:°|deg)?\s*(?:N)\b",
        r"(?i)\b(\d{1,3}(?:\.\d+)?)\s*(?:N)\b",
        r"(?i)\b(\d{1,3}(?:\.\d+)?)\s*[,;]\s*(\d{2,6})\s*(?:N)\b",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            value = match.group(1)
            return value
    return ""


def extract_longitude(text: str) -> str:
    patterns = [
        r"(?i)\b(\d{1,3}(?:\.\d+)?)\s*(?:°|deg)?\s*(?:E|W)\b",
        r"(?i)\b(\d{1,3}(?:\.\d+)?)\s*(?:E|W)\b",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1)
    return ""


def extract_numeric_hint(text: str, field_name: str) -> str:
    patterns = {
        "raw_area": r"(?:area|extent)\s*[:\-]?\s*(\d+(?:\.\d+)?)",
        "raw_length": r"(?:length|runout)\s*[:\-]?\s*(\d+(?:\.\d+)?)",
        "raw_width": r"(?:width|breadth)\s*[:\-]?\s*(\d+(?:\.\d+)?)",
        "raw_volume": r"(?:volume)\s*[:\-]?\s*(\d+(?:\.\d+)?)",
        "raw_landslide_type": r"(?:landslide type|failure type|type)\s*[:\-]?\s*([A-Za-z .'-]+)",
        "raw_trigger": r"(?:trigger|cause)\s*[:\-]?\s*([A-Za-z .'-]+)",
    }
    pattern = patterns.get(field_name)
    if not pattern:
        return ""
    match = re.search(pattern, text, flags=re.IGNORECASE)
    if match:
        return normalize_whitespace(match.group(1))
    return ""


def extract_aggregate_statistics(text: str, source_file: str, page_number: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for match in re.finditer(r"(?P<count>\d{1,3}(?:[ ,]\d{3})*)\s+(?:landslides?|events?)\b", text, flags=re.IGNORECASE):
        count_value = match.group("count").replace(",", "")
        state = detect_state_in_text(text)
        district = extract_district_hint(text)
        rows.append(
            {
                "source_file": source_file,
                "page_number": page_number,
                "state": state,
                "district": district,
                "reported_count": int(count_value),
                "description": normalize_whitespace(text[:280]),
            }
        )
    return rows


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


def write_csv(path: Path, fieldnames: Iterable[str], rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fieldnames))
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def inspect_pdf(pdf_path: Path, sample_pages: int = 5) -> dict[str, Any]:
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    with fitz.open(str(pdf_path)) as document:
        total_pages = document.page_count
        sample_range = min(sample_pages, total_pages)
        pages_with_text = 0
        pages_without_text = 0
        tables_detected = 0
        text_lengths: list[int] = []

        for page_index in range(sample_range):
            page = document.load_page(page_index)
            text = page.get_text("text")
            text_lengths.append(len(text.strip()))
            if text and text.strip():
                pages_with_text += 1
            else:
                pages_without_text += 1

            try:
                table_finder = page.find_tables()
            except Exception:
                table_finder = None
            if table_finder is not None:
                try:
                    table_count = len(table_finder.tables())
                except Exception:
                    table_count = 0
                tables_detected += table_count

        scanned_or_image_only = pages_with_text == 0 and total_pages > 0
        text_extraction_ratio = (pages_with_text / sample_range) if sample_range else 0.0
        extractability = "text-based" if text_extraction_ratio >= 0.5 else "likely scanned or image-only"

        metadata = document.metadata
        return {
            "source_file": pdf_path.name,
            "file_size_bytes": pdf_path.stat().st_size,
            "page_count": total_pages,
            "sample_pages_checked": sample_range,
            "pages_with_text": pages_with_text,
            "pages_without_text": pages_without_text,
            "tables_detected": tables_detected,
            "scanned_or_image_only": scanned_or_image_only,
            "pdf_metadata": {key: value for key, value in metadata.items() if value is not None},
            "text_extraction_ratio": round(text_extraction_ratio, 4),
            "text_extraction_summary": extractability,
            "sample_text_lengths": text_lengths,
        }


def extract_pdf_text(pdf_path: Path, output_dir: Path | None = None) -> list[dict[str, Any]]:
    output_dir = output_dir or RAW_TEXT_DIR
    ensure_directories()
    rows: list[dict[str, Any]] = []
    aggregate_rows: list[dict[str, Any]] = []

    with fitz.open(str(pdf_path)) as document:
        for page_number in range(document.page_count):
            page = document.load_page(page_number)
            page_text = page.get_text("text")
            file_name = f"page_{page_number + 1:03d}.txt"
            text_path = output_dir / file_name
            text_path.write_text(page_text or "", encoding="utf-8")

            raw_state = detect_state_in_text(page_text)
            raw_district = extract_district_hint(page_text)
            raw_location = extract_location_hint(page_text)
            raw_date = extract_date_hint(page_text)
            raw_latitude = extract_latitude(page_text)
            raw_longitude = extract_longitude(page_text)
            raw_landslide_type = extract_numeric_hint(page_text, "raw_landslide_type")
            raw_trigger = extract_numeric_hint(page_text, "raw_trigger")
            raw_area = extract_numeric_hint(page_text, "raw_area")
            raw_length = extract_numeric_hint(page_text, "raw_length")
            raw_width = extract_numeric_hint(page_text, "raw_width")
            raw_volume = extract_numeric_hint(page_text, "raw_volume")

            row = {
                "source_file": pdf_path.name,
                "page_number": page_number + 1,
                "record_index": 1,
                "raw_text": page_text,
                "raw_state": raw_state,
                "raw_district": raw_district,
                "raw_location": raw_location,
                "raw_date": raw_date,
                "raw_latitude": raw_latitude,
                "raw_longitude": raw_longitude,
                "raw_landslide_type": raw_landslide_type,
                "raw_trigger": raw_trigger,
                "raw_area": raw_area,
                "raw_length": raw_length,
                "raw_width": raw_width,
                "raw_volume": raw_volume,
                "data_status": "OBSERVED" if page_text.strip() else "NOT_AVAILABLE",
                "source_name": "GSI",
                "source_file_name": pdf_path.name,
                "source_page": page_number + 1,
                "extraction_method": "PyMuPDF",
                "extraction_timestamp": datetime.now(timezone.utc).isoformat(),
            }
            rows.append(row)
            aggregate_rows.extend(extract_aggregate_statistics(page_text, pdf_path.name, page_number + 1))

            try:
                table_data = page.find_tables()
            except Exception:
                table_data = []
            if table_data:
                for table_index, table in enumerate(table_data, start=1):
                    csv_path = GSI_TABLES_DIR / f"{pdf_path.stem}_page_{page_number + 1:03d}_table_{table_index}.csv"
                    try:
                        table_df = table.to_pandas()
                        table_df.to_csv(csv_path, index=False)
                    except Exception:
                        LOGGER.warning("Table extraction failed for page %s table %s", page_number + 1, table_index)

    raw_csv_path = GSI_EXTRACTED_DIR / f"{pdf_path.stem}_raw_extraction.csv"
    fieldnames = [
        "source_file",
        "page_number",
        "record_index",
        "raw_text",
        "raw_state",
        "raw_district",
        "raw_location",
        "raw_date",
        "raw_latitude",
        "raw_longitude",
        "raw_landslide_type",
        "raw_trigger",
        "raw_area",
        "raw_length",
        "raw_width",
        "raw_volume",
        "data_status",
        "source_name",
        "source_file_name",
        "source_page",
        "extraction_method",
        "extraction_timestamp",
    ]
    write_csv(raw_csv_path, fieldnames, rows)

    aggregate_stats_path = GSI_EXTRACTED_DIR / "aggregate_statistics.csv"
    aggregate_fieldnames = ["source_file", "page_number", "state", "district", "reported_count", "description"]
    write_csv(aggregate_stats_path, aggregate_fieldnames, aggregate_rows)

    return rows


def normalize_record_row(raw_row: dict[str, Any]) -> dict[str, Any]:
    raw_text = str(raw_row.get("raw_text", ""))
    normalized = {
        "source_file": raw_row.get("source_file", ""),
        "page_number": raw_row.get("page_number", ""),
        "record_index": raw_row.get("record_index", 1),
        "raw_text": raw_text,
        "raw_state": raw_row.get("raw_state", ""),
        "raw_district": raw_row.get("raw_district", ""),
        "raw_location": raw_row.get("raw_location", ""),
        "raw_date": raw_row.get("raw_date", ""),
        "raw_latitude": raw_row.get("raw_latitude", ""),
        "raw_longitude": raw_row.get("raw_longitude", ""),
        "state": normalize_whitespace(raw_row.get("raw_state", "")) or "",
        "district": normalize_whitespace(raw_row.get("raw_district", "")) or "",
        "location": normalize_whitespace(raw_row.get("raw_location", "")) or "",
        "date": normalize_date(raw_row.get("raw_date", "")),
        "latitude": parse_float(raw_row.get("raw_latitude", "")),
        "longitude": parse_float(raw_row.get("raw_longitude", "")),
        "landslide_type": normalize_whitespace(raw_row.get("raw_landslide_type", "")) or "",
        "trigger": normalize_whitespace(raw_row.get("raw_trigger", "")) or "",
        "area": normalize_whitespace(raw_row.get("raw_area", "")) or "",
        "length": normalize_whitespace(raw_row.get("raw_length", "")) or "",
        "width": normalize_whitespace(raw_row.get("raw_width", "")) or "",
        "volume": normalize_whitespace(raw_row.get("raw_volume", "")) or "",
        "data_status": "OBSERVED" if raw_text.strip() else "NOT_AVAILABLE",
        "source_name": "GSI",
        "source_file": raw_row.get("source_file", ""),
        "source_page": raw_row.get("source_page", raw_row.get("page_number", "")),
        "extraction_method": raw_row.get("extraction_method", "PyMuPDF"),
        "extraction_timestamp": raw_row.get("extraction_timestamp", datetime.now(timezone.utc).isoformat()),
        "is_valid_state": False,
        "is_valid_coordinates": False,
        "is_valid_record": False,
        "notes": "",
    }

    normalized["state"] = normalize_whitespace(normalized["state"])
    normalized["district"] = normalize_whitespace(normalized["district"])
    normalized["location"] = normalize_whitespace(normalized["location"])

    if normalized["state"] and normalized["state"] in NER_STATES:
        normalized["is_valid_state"] = True
    elif normalized["state"]:
        normalized["notes"] = "State outside approved NER states."

    latitude = normalized["latitude"]
    longitude = normalized["longitude"]
    if latitude is not None and longitude is not None:
        valid_lat = -90 <= latitude <= 90
        valid_lon = -180 <= longitude <= 180
        normalized["is_valid_coordinates"] = valid_lat and valid_lon
        if not (valid_lat and valid_lon):
            normalized["notes"] = "Invalid latitude/longitude coordinates."
    else:
        normalized["notes"] = "Latitude/longitude not explicitly present."

    normalized["is_valid_record"] = bool(normalized["is_valid_state"] or not normalized["state"]) and (normalized["is_valid_coordinates"] or latitude is None or longitude is None)

    if normalized["state"] and not normalized["is_valid_state"]:
        normalized["data_status"] = "NOT_AVAILABLE"

    return normalized


def normalize_records(csv_path: Path, output_path: Path | None = None) -> list[dict[str, Any]]:
    if not csv_path.exists():
        raise FileNotFoundError(f"Raw extraction CSV not found: {csv_path}")

    output_path = output_path or GSI_EXTRACTED_DIR / "normalized_gsi_records.csv"
    rows: list[dict[str, Any]] = []
    with csv_path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for raw_row in reader:
            normalized = normalize_record_row(raw_row)
            rows.append(normalized)

    fieldnames = [
        "source_file",
        "page_number",
        "record_index",
        "raw_text",
        "raw_state",
        "raw_district",
        "raw_location",
        "raw_date",
        "raw_latitude",
        "raw_longitude",
        "state",
        "district",
        "location",
        "date",
        "latitude",
        "longitude",
        "landslide_type",
        "trigger",
        "area",
        "length",
        "width",
        "volume",
        "data_status",
        "source_name",
        "source_page",
        "extraction_method",
        "extraction_timestamp",
        "is_valid_state",
        "is_valid_coordinates",
        "is_valid_record",
        "notes",
    ]
    write_csv(output_path, fieldnames, rows)

    total_pages = max((int(row.get("page_number", 0)) for row in rows), default=0)
    pages_with_text = sum(1 for row in rows if row.get("raw_text", "").strip())
    pages_without_text = max(total_pages - pages_with_text, 0)
    rows_with_coordinates = sum(1 for row in rows if row.get("latitude") is not None and row.get("longitude") is not None)
    rows_without_coordinates = len(rows) - rows_with_coordinates
    rows_with_dates = sum(1 for row in rows if row.get("date"))
    rows_with_state = sum(1 for row in rows if row.get("state"))
    rows_in_ner = sum(1 for row in rows if row.get("state") in NER_STATES)
    rows_outside_ner = sum(1 for row in rows if row.get("state") and row.get("state") not in NER_STATES)
    invalid_coordinates = sum(1 for row in rows if row.get("latitude") is not None and row.get("longitude") is not None and not row.get("is_valid_coordinates"))
    duplicate_candidates = 0
    seen = set()
    for row in rows:
        key = (row.get("state"), row.get("district"), row.get("location"), row.get("date"), row.get("page_number"))
        if key in seen:
            duplicate_candidates += 1
        seen.add(key)
    extraction_failures = sum(1 for row in rows if row.get("data_status") == "NOT_AVAILABLE")

    validation_report = {
        "total_pages": total_pages,
        "pages_with_text": pages_with_text,
        "pages_without_text": pages_without_text,
        "tables_detected": 0,
        "rows_extracted": len(rows),
        "rows_with_coordinates": rows_with_coordinates,
        "rows_without_coordinates": rows_without_coordinates,
        "rows_with_dates": rows_with_dates,
        "rows_with_state": rows_with_state,
        "rows_in_ner": rows_in_ner,
        "rows_outside_ner": rows_outside_ner,
        "invalid_coordinates": invalid_coordinates,
        "duplicate_candidates": duplicate_candidates,
        "extraction_failures": extraction_failures,
    }
    write_json(VALIDATION_REPORT_PATH, validation_report)
    return rows


def detect_text_based_document(pdf_path: Path | None) -> bool:
    if pdf_path is None:
        return False
    summary = inspect_pdf(pdf_path, sample_pages=10)
    return summary["pages_with_text"] > 0 and not summary["scanned_or_image_only"]
