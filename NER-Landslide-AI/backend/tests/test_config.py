from __future__ import annotations

from backend.app.config import NER_STATES, get_settings


def test_ner_states_count() -> None:
    assert len(NER_STATES) == 8
    assert NER_STATES == (
        "Arunachal Pradesh",
        "Assam",
        "Manipur",
        "Meghalaya",
        "Mizoram",
        "Nagaland",
        "Sikkim",
        "Tripura",
    )


def test_settings_database_name() -> None:
    settings = get_settings()
    assert "ner_landslide" in settings.database_url
