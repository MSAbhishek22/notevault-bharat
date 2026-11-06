"""Tests: Vercel entrypoint (api/index.py) serves the real app.

Loads api/index.py exactly as Vercel would — the `application` WSGI
callable bound to the default agent over the repo's real notes folder
(5 notes, mock mode, no key) — and drives it over real HTTP via
wsgiref. Also checks vercel.json rewrites every path to /api/index.
"""
import importlib.util
import json
import threading
import urllib.error
import urllib.request
from pathlib import Path
from wsgiref.simple_server import make_server as make_wsgi_server

import pytest

_REPO = Path(__file__).resolve().parent.parent


def _load_entrypoint():
    spec = importlib.util.spec_from_file_location(
        "vercel_index", _REPO / "api" / "index.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.application


@pytest.fixture(scope="module")
def live():
    server = make_wsgi_server("127.0.0.1", 0, _load_entrypoint())
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


def test_vercel_entrypoint_exposes_wsgi_application():
    assert callable(_load_entrypoint())


def test_vercel_json_rewrites_everything_to_api_index():
    cfg = json.loads((_REPO / "vercel.json").read_text(encoding="utf-8"))
    assert cfg["rewrites"] == [
        {"source": "/(.*)", "destination": "/api/index"}]


def test_vercel_homepage_serves_ui(live):
    status, body = _get(live, "/")
    assert status == 200
    assert b"NoteVault Bharat" in body


def test_vercel_status_mock_mode_five_notes(live):
    status, body = _get(live, "/api/status")
    assert status == 200
    data = json.loads(body)
    assert data["mode"] == "mock"
    assert data["notes_count"] == 5
    assert data["model"] == "qwen-3.8-27b"


def test_vercel_ask_mock_answer_and_refusal(live):
    status, body = _post(live, "/api/ask", {"question": "What is Abhiverse for?"})
    assert status == 200
    data = json.loads(body)
    assert data["refused"] is False
    assert "[mock]" in data["answer"]
    status, body = _post(live, "/api/ask", {"question": "quantum bananas"})
    assert status == 200
    assert json.loads(body)["refused"] is True
