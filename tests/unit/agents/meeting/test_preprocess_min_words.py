"""Preprocess: umbral de palabras (spec 013)."""

from unittest.mock import patch

from src.agents.meeting.nodes.preprocess.node import preprocess_node


def test_short_text_adds_warning() -> None:
    with patch("src.agents.meeting.nodes.preprocess.node.get_meeting_min_words", return_value=20):
        out = preprocess_node({"raw_text": "uno dos tres cuatro cinco"})
    assert "processing_errors" in out
    assert out["processing_errors"]
    assert "20" in out["processing_errors"][0]
    assert out["raw_text"] == "uno dos tres cuatro cinco"


def test_long_enough_no_warning() -> None:
    words = " ".join(f"w{i}" for i in range(25))
    with patch("src.agents.meeting.nodes.preprocess.node.get_meeting_min_words", return_value=20):
        out = preprocess_node({"raw_text": words})
    assert "processing_errors" not in out
    assert out["raw_text"] == words
