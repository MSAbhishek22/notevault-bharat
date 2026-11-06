"""WSGI entry point for NoteVault Bharat — PythonAnywhere free tier.

Stdlib only. PythonAnywhere free web apps must be WSGI: they cannot run
a long-lived ThreadingHTTPServer on a port, so `python3 run.py serve`
cannot run there as-is. This module exposes the same app over WSGI.

The route table mirrors NoteVaultBharatHandler in web.py exactly
(GET /, /api/status, /api/note; POST /api/ask, /api/organise,
/api/reset-budget), calling the same NotesAgent methods with the same
error mapping, so the live app behaves identically to the local
server. web.py is untouched by this module.

Agent construction: config_from_env(), with the notes folder resolved
from this package's location unless NOTES_ROOT is set — uWSGI workers
do not start in the repo directory, so a relative "notes" would fail.
No key is needed: without BHARATCODE_API_KEY the provider is mock and
every answer is labelled [mock], exactly as locally.

Live-mode note: on PythonAnywhere free accounts outbound HTTP is
allowlist-only. Real BharatCode calls need bharatcode.ai allowlisted
(see deployment/PYTHONANYWHERE_DEPLOY.md); until then the deployed app
runs in mock mode and any real-mode attempt fails honestly with a
provider error — it never pretends a mock answer is real.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from urllib.parse import parse_qs

from .agent import NotesAgent
from .config import config_from_env
from .web import PAGE

_MAX_BODY = 64_000  # same cap as the stdlib handler in web.py
_REASONS = {200: "OK", 400: "Bad Request", 404: "Not Found"}


def _to_json(obj: dict) -> bytes:
    return json.dumps(obj).encode("utf-8")


def _default_agent() -> NotesAgent:
    notes_root = os.environ.get("NOTES_ROOT")
    if not notes_root:
        notes_root = str(Path(__file__).resolve().parent.parent / "notes")
    return NotesAgent(config_from_env(Path(notes_root)))


def _dispatch(agent: NotesAgent, method: str, path: str, query: str,
              body_bytes: bytes) -> tuple[int, str, bytes]:
    """Pure route dispatch. Returns (status, content-type, body bytes)."""
    if method == "GET" and path == "/":
        data = PAGE.encode("utf-8")
        return 200, "text/html; charset=utf-8", data
    if method == "GET" and path == "/api/status":
        return 200, "application/json", _to_json(agent.status_dict())
    if method == "GET" and path == "/api/note":
        rel = parse_qs(query).get("path", [""])[0]
        try:
            note = agent.get_note(rel)
        except (FileNotFoundError, ValueError) as exc:
            return 404, "application/json", _to_json({"error": str(exc)})
        return 200, "application/json", _to_json({
            "title": note.title, "rel_path": note.rel_path,
            "tags": note.tags, "body": note.body[:8000],
        })
    if method == "POST":
        try:
            body = json.loads(body_bytes.decode("utf-8")) if body_bytes.strip() else {}
        except (ValueError, json.JSONDecodeError) as exc:
            return 400, "application/json", _to_json({"error": str(exc)})
        try:
            if path == "/api/ask":
                question = str(body.get("question") or "").strip()
                if not question:
                    return 400, "application/json", _to_json({"error": "question is required"})
                result = agent.ask_detailed(
                    question, model=body.get("model") or None,
                    language=body.get("language") or None)
                return 200, "application/json", _to_json(result.to_dict())
            if path == "/api/organise":
                return 200, "application/json", _to_json({"plan": agent.organise_plan()})
            if path == "/api/reset-budget":
                agent.reset_budget()
                return 200, "application/json", _to_json({"budget": agent.budget.to_dict()})
        except (ValueError, RuntimeError) as exc:
            # ValueError: bad model id / language / path. RuntimeError:
            # budget, provider failure. Never include key values: these
            # messages come from our own code, not env.
            return 400, "application/json", _to_json({"error": str(exc)})
    return 404, "application/json", _to_json({"error": "Not found"})


def make_application(agent: NotesAgent | None = None):
    """Build the WSGI callable. Tests pass a seeded agent; production
    uses the default agent built from the environment."""
    bound = agent if agent is not None else _default_agent()

    def application(environ, start_response):
        method = environ.get("REQUEST_METHOD", "GET")
        path = environ.get("PATH_INFO", "/")
        query = environ.get("QUERY_STRING", "")
        try:
            length = int(environ.get("CONTENT_LENGTH") or 0)
        except ValueError:
            length = 0
        if length > _MAX_BODY:
            status, ctype, body = 400, "application/json", _to_json({"error": "Request too large"})
        else:
            raw = environ["wsgi.input"].read(length) if length else b""
            status, ctype, body = _dispatch(bound, method, path, query, raw)
        start_response(
            f"{status} {_REASONS.get(status, '')}",
            [("Content-Type", ctype), ("Content-Length", str(len(body)))],
        )
        return [body]

    return application


# What PythonAnywhere imports: `from notes_bharat.wsgi import application`.
application = make_application()
