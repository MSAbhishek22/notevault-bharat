"""Vercel entrypoint — re-exports the WSGI app as one serverless function.

Vercel's Python runtime detects `application` as a WSGI callable in
api/index.py. All routes (GET /, /api/status, /api/note; POST /api/ask,
/api/organise, /api/reset-budget) run through notes_bharat.wsgi — the
same adapter as the PythonAnywhere deploy — so the live app behaves
identically to the local server. vercel.json rewrites every path to
this function. No framework, no dependencies: stdlib only.

Honest difference from the local server: the budget counter lives in
memory on the agent this module builds at import. On Vercel it resets
on every cold start and can diverge across concurrent warm instances,
so it is demo-only, never durable state. See
deployment/OAUTH_HOST.md.
"""
from notes_bharat.wsgi import application

__all__ = ["application"]
