"""Tests: WSGI adapter (PythonAnywhere path) mirrors the stdlib server.

Drives notes_bharat.wsgi.application over real HTTP via wsgiref, with a
seeded mock agent — no network, no key. Every route the stdlib handler
serves must answer identically here.
"""
import json
import threading
import urllib.error
import urllib.request
from wsgiref.simple_server import make_server as make_wsgi_server

import pytest

from notes_bharat.agent import NotesAgent
from notes_bharat.config import Config
from notes_bharat.wsgi import make_application


def _config(tmp_path, **overrides):
    kwargs = dict(notes_root=tmp_path, provider="mock")
    kwargs.update(overrides)
    return Config(**kwargs)


def _seed(tmp_path):
    (tmp_path / "a.md").write_text("# Abhiverse idea\nPhone remote for laptop. #project", encoding="utf-8")


@pytest.fixture()
def live(tmp_path):
    _seed(tmp_path)
    agent = NotesAgent(_config(tmp_path))
    server = make_wsgi_server("127.0.0.1", 0, make_application(agent))
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{port}"
    server.shutdown()
    server.server_close()


def _get(base, path):
    with urllib.request.urlopen(base + path) as resp:
        return resp.status, resp.read()


def _post(base, path, obj):
    req = urllib.request.Request(
        base + path, data=json.dumps(obj).encode("utf-8"),
        headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req) as resp:
        return resp.status, resp.read()


def _post_err(base, path, obj):
    req = urllib.request.Request(
        base + path, data=json.dumps(obj).encode("utf-8"),
        headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, resp.read()
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read()


def test_wsgi_homepage_serves_ui(live):
    status, body = _get(live, "/")
    assert status == 200
    assert b"NoteVault Bharat" in body
    assert b"galaxy" in body


def test_wsgi_status_mock_mode(live):
    status, body = _get(live, "/api/status")
    assert status == 200
    data = json.loads(body)
    assert data["mode"] == "mock"
    assert data["notes_count"] == 1
    assert data["model"] == "qwen-3.8-27b"


def test_wsgi_note_and_missing_note(live):
    status, body = _get(live, "/api/note?path=a.md")
    assert status == 200
    data = json.loads(body)
    assert data["title"] == "Abhiverse idea"
    assert "Phone remote" in data["body"]
    try:
        _get(live, "/api/note?path=nope.md")
    except urllib.error.HTTPError as exc:
        assert exc.code == 404
    else:  # pragma: no cover
        raise AssertionError("missing note must 404")


def test_wsgi_ask_mock_answer_and_refusal(live):
    status, body = _post(live, "/api/ask", {"question": "What is Abhiverse for?"})
    assert status == 200
    data = json.loads(body)
    assert data["refused"] is False
    assert "[mock]" in data["answer"]
    status, body = _post(live, "/api/ask", {"question": "quantum bananas"})
    assert status == 200
    assert json.loads(body)["refused"] is True


def test_wsgi_ask_requires_question(live):
    status, body = _post_err(live, "/api/ask", {})
    assert status == 400
    assert b"question is required" in body


def test_wsgi_organise_and_reset_budget(live):
    status, body = _post(live, "/api/organise", {})
    assert status == 200
    assert "plan" in json.loads(body)
    status, body = _post(live, "/api/reset-budget", {})
    assert status == 200
    assert json.loads(body)["budget"]["used"] == 0


def test_wsgi_unknown_route_404(live):
    try:
        _get(live, "/nope")
    except urllib.error.HTTPError as exc:
        assert exc.code == 404
    else:  # pragma: no cover
        raise AssertionError("unknown route must 404")
