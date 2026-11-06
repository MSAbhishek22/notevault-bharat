"""Tests: Vercel entrypoint serves the real app with original paths.

Vercel's Python runtime loads the app from the entrypoint declared in
pyproject.toml ([tool.vercel] entrypoint) and routes every request to
it, so the app sees the original request path — no vercel.json rewrite
is involved. A rewrite to /api/index used to mask every path as
PATH_INFO=/api/index and made the live app 404 on /, /api/status and
everything else; that failure mode is pinned in
tests/test_vercel_routing_regression.py, and the diagnosis is in
deployment/VERCEL_ROUTING_FIX.md.
"""
import importlib
import json
import threading
import tomllib
import urllib.request
from pathlib import Path
from wsgiref.simple_server import make_server as make_wsgi_server

import pytest

_REPO = Path(__file__).resolve().parent.parent
_ENTRYPOINT = "notes_bharat.wsgi:application"


def _declared_entrypoint():
    with (_REPO / "pyproject.toml").open("rb") as fh:
        cfg = tomllib.load(fh)
    return cfg["tool"]["vercel"]["entrypoint"]


def _load_entrypoint():
    module_name, attr = _declared_entrypoint().split(":", 1)
    module = importlib.import_module(module_name)
    return getattr(module, attr)


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


def test_vercel_entrypoint_declared_in_pyproject():
    assert _declared_entrypoint() == _ENTRYPOINT


def test_vercel_entrypoint_resolves_to_callable_wsgi_app():
    assert callable(_load_entrypoint())


def test_vercel_json_has_no_rewrites():
    cfg = json.loads((_REPO / "vercel.json").read_text(encoding="utf-8"))
    assert "rewrites" not in cfg


def test_vercel_api_shim_is_gone():
    # api/index.py was a second function that the old rewrite pointed
    # at; keeping it would leave two entrypoints and a double route
    # for /api/index. The app has exactly one entrypoint now.
    assert not (_REPO / "api" / "index.py").exists()


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
