from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env", override=False)

NER_STATES: tuple[str, ...] = (
    "Arunachal Pradesh",
    "Assam",
    "Manipur",
    "Meghalaya",
    "Mizoram",
    "Nagaland",
    "Sikkim",
    "Tripura",
)


@dataclass
class Settings:
    project_root: Path = field(default_factory=lambda: PROJECT_ROOT)
    app_name: str = os.getenv("APP_NAME", "NER Landslide AI")
    app_env: str = os.getenv("APP_ENV", "development")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    data_dir: Path = field(default_factory=lambda: PROJECT_ROOT / "data")
    raw_data_dir: Path = field(default_factory=lambda: PROJECT_ROOT / "data" / "raw")
    processed_data_dir: Path = field(default_factory=lambda: PROJECT_ROOT / "data" / "processed")
    training_data_dir: Path = field(default_factory=lambda: PROJECT_ROOT / "data" / "training")
    default_crs: str = os.getenv("DEFAULT_CRS", "EPSG:4326")
    target_crs: str = os.getenv("TARGET_CRS", "EPSG:32646")
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://postgres:postgres@localhost:5432/ner_landslide_ai",
    )
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("API_PORT", "8000"))


SETTINGS = Settings()


def get_settings() -> Settings:
    return SETTINGS
