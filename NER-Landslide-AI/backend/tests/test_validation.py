from __future__ import annotations

from backend.app.validation import is_valid_ner_state, validate_ner_state, validate_record_state


def test_valid_ner_state() -> None:
    assert is_valid_ner_state("Meghalaya") is True
    assert is_valid_ner_state("Delhi") is False


def test_validate_ner_state_rejects_non_ner() -> None:
    valid, message = validate_ner_state("Karnataka")
    assert valid is False
    assert "outside the approved NER states" in (message or "")


def test_validate_record_state() -> None:
    ok, issues = validate_record_state({"state": "Assam"})
    assert ok is True
    assert issues == []

    ok, issues = validate_record_state({"state": "Punjab"})
    assert ok is False
    assert any("approved NER states" in issue for issue in issues)
