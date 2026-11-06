"""Regression tests: the Vercel rewrite bug (Nov 2026).

The first Vercel deploy used vercel.json {"rewrites": [{"source":
"/(.*)", "destination": "/api/index"}]}. Vercel's proxy then delivered
every request to the function with PATH_INFO=/api/index, and the app —
which routes on PATH_INFO — answered its own 404 JSON for /, /api/status
and every other path, even though the function was running. Vercel
provides no header or environ value carrying the original path to a
rewritten function (its request-headers doc lists only host/IP/geo/
deployment headers; the vercel-runtime source builds PATH_INFO from
the request line and has no rewrite handling), so the fix is to not
rewrite at all: the app is a root entrypoint ([tool.vercel] entrypoint)
and Vercel routes every request to it with the original path. The
entrypoint mechanism itself is the "original-path mechanism". See
deployment/VERCEL_ROUTING_FIX.md.
"""
import importlib
import json
import threading
import tomllib
import urllib.error
import urllib.request
from pathlib import Path
from wsgiref.simple_server import make_server as make_wsgi_server

import pytest

_REPO = Path(__file__).resolve().parent.parent


def _load_entrypoint():
    with (_REPO / "pyproject.toml").open("rb") as fh:
        entrypoint = tomllib.load(fh)["tool"]["vercel"]["entrypoint"]
    module_name, attr = entrypoint.split(":", 1)
    return getattr(importlib.import_module(module_name), attr)


def _rewritten_to_api_index(app):
    """WSGI middleware simulating Vercel's old rewrite: every request
    arrives with PATH_INFO=/api/index, whatever the client asked for."""
    def rewritten(environ, start_response):
        environ["PATH_INFO"] = "/api/index"
        return app(environ, start_response)
    return rewritten


def _serve(app):
    server = make_wsgi_server("127.0.0.1", 0, app)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, f"http://127.0.0.1:{port}"


@pytest.fixture(scope="module")
def live():
    server, base = _serve(_load_entrypoint())
    yield base
    server.shutdown()
    server.server_close()


@pytest.fixture(scope="module")
def live_rewritten():
    # The broken deployment, reproduced locally: the entrypoint behind
    # the old /(.*) -> /api/index rewrite.
    server, base = _serve(_rewritten_to_api_index(_load_entrypoint()))
    yield base
    server.shutdown()
    server.server_close()


def _fetch(base, path, method="GET", obj=None):
    data = json.dumps(obj).encode("utf-8") if obj is not None else None
    headers = {"Content-Type": "application/json"} if data else {}
    req = urllib.request.Request(
        base + path, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, resp.read()
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read()


def test_old_rewrite_masked_homepage_and_status(live_rewritten):
    # The exact live symptom, pinned: with PATH_INFO forced to
    # /api/index the app 404s on / and /api/status. If a rewrite ever
    # returns, this is what the live site does again.
    for path in ("/", "/api/status"):
        status, body = _fetch(live_rewritten, path)
        assert status == 404
        assert json.loads(body) == {"error": "Not found"}


def test_entrypoint_serves_original_paths(live):
    status, body = _fetch(live, "/")
    assert status == 200
    assert b"NoteVault Bharat" in body
    status, body = _fetch(live, "/api/status")
    assert status == 200
    data = json.loads(body)
    assert data["mode"] == "mock"
    assert data["notes_count"] == 5
    assert data["model"] == "qwen-3.8-27b"


def test_entrypoint_ask_and_refusal(live):
    status, body = _fetch(
        live, "/api/ask", method="POST",
        obj={"question": "What is Abhiverse for?"})
    assert status == 200
    data = json.loads(body)
    assert data["refused"] is False
    assert "[mock]" in data["answer"]
    status, body = _fetch(
        live, "/api/ask", method="POST", obj={"question": "quantum bananas"})
    assert status == 200
    assert json.loads(body)["refused"] is True


def test_api_index_direct_request_does_not_break_routing(live):
    # /api/index is no longer a function route — just an unknown path
    # to the single app. It must answer the app's own 404, not break,
    # and the next real request must still route normally.
    status, body = _fetch(live, "/api/index")
    assert status == 404
    assert json.loads(body) == {"error": "Not found"}
    status, body = _fetch(live, "/api/status")
    assert status == 200
    assert json.loads(body)["mode"] == "mock"
