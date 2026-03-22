"""Codec processing_errors (spec 013)."""

import json

from src.db.processing_errors_codec import decode_processing_errors, encode_processing_errors


def test_encode_decode_round_trip() -> None:
    msgs = ["a", "b con ñ"]
    raw = encode_processing_errors(msgs)
    assert raw is not None
    assert decode_processing_errors(raw) == msgs


def test_encode_empty() -> None:
    assert encode_processing_errors([]) is None
    assert decode_processing_errors(None) == []
    assert decode_processing_errors("") == []


def test_decode_legacy_plain_string() -> None:
    assert decode_processing_errors("Transcripción no disponible") == ["Transcripción no disponible"]


def test_decode_legacy_json_string_value() -> None:
    raw = json.dumps("solo", ensure_ascii=False)
    assert decode_processing_errors(raw) == ["solo"]
