"""Tests del cliente SSE (UI)."""

from src.ui.sse_client import iter_sse_events


class _FakeResponse:
    def __init__(self, chunks: list[str]) -> None:
        self._chunks = chunks

    def iter_text(self):
        yield from self._chunks


def test_iter_sse_events_single_chunk():
    body = '{"type": "phase", "phase": "received", "message": "ok"}\n\n'
    r = _FakeResponse([f"data: {body}"])
    events = list(iter_sse_events(r))
    assert len(events) == 1
    assert events[0]["type"] == "phase"
    assert events[0]["phase"] == "received"


def test_iter_sse_events_split_across_chunks():
    r = _FakeResponse(
        [
            'data: {"type":"comp',
            'lete","data":{"participants":"x"}}\n\n',
        ]
    )
    events = list(iter_sse_events(r))
    assert len(events) == 1
    assert events[0]["type"] == "complete"
