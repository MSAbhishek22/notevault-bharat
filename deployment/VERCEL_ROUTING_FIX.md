# Vercel routing fix — NoteVault Bharat

**Date:** Fri 6 Nov 2026. **Status: FIXED LOCALLY, NOT PUSHED, NOT
DEPLOYED.** The live deployment still serves the broken build.

## Symptom (live, 6 Nov 18:46 IST)

Deployment `EoWHmRM7qNxjyenGTFiHQRyhVq7P` is Ready at
https://notevault-bharat.vercel.app, the Python function IS running,
but every path returns the app's own 404 JSON `{"error": "Not found"}` —
including `/` and `/api/status`.

## Confirmed diagnosis

`vercel.json` rewrote every path to the function:

```json
{"rewrites": [{"source": "/(.*)", "destination": "/api/index"}]}
```

Vercel's proxy then delivered every request to the function with the
request line `/api/index`, so the WSGI app — which routes on
`PATH_INFO` — saw `/api/index` for every request and 404'd. The build
log's warning matches: internal rewrites in backend-framework projects
now route using the rewritten destination path.

**There is no Vercel-provided way to recover the original path inside
a rewritten `/api` function** — verified, not assumed:

- Vercel's request-headers doc lists only host/IP/geo/deployment
  headers (`host`, `x-vercel-id`, `x-forwarded-host`,
  `x-forwarded-proto`, `x-real-ip`, `x-forwarded-for`,
  `x-vercel-deployment-url`, geo headers). No header carries the
  original request path.
  (https://examples.vercel.com/docs/headers/request-headers)
- The `vercel-runtime` source (vercel/vercel,
  `python/vercel-runtime/src/vercel_runtime/`) runs a vendored uvicorn
  server: the ASGI scope — and therefore WSGI `PATH_INFO` — is built
  from the HTTP request line the proxy sends. The runtime contains no
  rewrite or original-path handling (zero matches for "rewrite"), and
  it strips `x-vercel-internal-*` headers before the app sees them.
- Empirically, the live site 404s on every path while the function
  runs — the app provably receives `/api/index`, not the real path.

## The fix (documented-correct, not a hack)

Use the Python runtime's entrypoint mechanism instead of a rewrite.
Vercel's Python runtime docs: "Define a supported Python entrypoint
so Vercel can load your application. Vercel then runs your app as
Vercel Functions and routes every request to it, so the app you run
locally deploys as-is."
(https://vercel.com/docs/functions/runtimes/python). The Flask guide
says the same for WSGI apps: the app becomes a single function from
the resolved entrypoint, configured with `tool.vercel.entrypoint` in
`pyproject.toml`.
(https://examples.vercel.com/docs/frameworks/backend/flask)

Changes (local only):

- `pyproject.toml` — added `[tool.vercel] entrypoint =
  "notes_bharat.wsgi:application"`. One entrypoint, one function.
- `vercel.json` — rewrites removed; now `{}` (no custom routing).
- `api/index.py` — DELETED (trashed, recoverable until 6 Dec 2026).
  It was the second function the old rewrite pointed at; keeping it
  would leave two entrypoints and a double route for `/api/index`.
- `notes_bharat/wsgi.py` — UNCHANGED. The app was correct; only the
  routing was wrong. All 6 routes and mock-mode behaviour are
  identical.
- `tests/test_vercel_entrypoint.py` — rewritten for the new model:
  entrypoint declared + resolvable, no rewrites, no `api/index.py`
  shim, homepage, status (mock, 5 notes), ask + refusal.
- `tests/test_vercel_routing_regression.py` — NEW, 4 tests: the old
  rewrite reproduced locally (PATH_INFO forced to `/api/index` → 404
  on `/` and `/api/status`), the entrypoint serving original paths,
  ask + refusal, and a direct GET `/api/index` answering the app's
  own 404 without breaking later routing.
- `deployment/OAUTH_HOST.md` — "What was built" / validation /
  next-steps updated to the entrypoint setup.

## Validation (Linux sandbox, Python 3.12.3, 6 Nov 2026)

- Full suite: **50/50 pytest PASS** (44 before the fix + 6 new/
  rewritten Vercel tests).
- A direct GET `/api/index` returns the app's 404 JSON and the next
  request still routes normally — no breakage, no double-route.

## Next steps (parent agent)

1. Push the fix to `MSAbhishek22/notevault-bharat` (user approval
   card required): `pyproject.toml`, `vercel.json`,
   `tests/test_vercel_entrypoint.py`,
   `tests/test_vercel_routing_regression.py`,
   `deployment/VERCEL_ROUTING_FIX.md`,
   `deployment/OAUTH_HOST.md` (updated). Verify the new head.
2. **Delete `api/index.py` on GitHub (web UI) in the same step.**
   Snapshot pushes do NOT delete files, so the stale shim would
   otherwise stay on the remote and Vercel would keep deploying the
   `/api/index` function alongside the entrypoint.
3. Wait for Vercel's Git auto-deploy, then verify the live URL:
   GET `/` → 200 with "NoteVault Bharat"; GET `/api/status` → 200,
   `mode` mock, `notes_count` 5; POST `/api/ask` "What is Abhiverse
   for?" → 200, `refused` false, `[mock]` in the answer; POST
   `/api/ask` "quantum bananas" → `refused` true. Record the URL +
   commit SHA in `deployment/RELEASE_MANIFEST.json`.
4. Only then record the demo video from the live URL.
5. PythonAnywhere remains the fallback if the user ever sets its
   password (WSGI adapter already built + pushed at `b4eff38`).
