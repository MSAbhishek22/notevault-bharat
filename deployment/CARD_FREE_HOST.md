# Card-free host for NoteVault Bharat — findings

**Date:** Fri 6 Nov 2026. **Verdict: PythonAnywhere free tier is the
only card-free GO.** Everything else checked is gated by a card, a
paid plan, or the wrong runtime shape. Research was read-only (public
web + official docs); nothing was created, signed into, or paid for.

## Ranking

| Host | Verdict | Why (evidence) |
|---|---|---|
| **PythonAnywhere free (Beginner)** | **GO** | Free account = email + username + password, no card (official pricing page + 2026 guides). 1 web app at `https://<username>.pythonanywhere.com`, free SSL, no idle sleep. **Needs a WSGI wrapper** (below) — free web apps must be WSGI. |
| Render free | BLOCKED | New account created 6 Nov via Google, but deploy demands a card even for the free tier (verified in the browser: "Add Card" modal on deploy; stopped, nothing charged). |
| Koyeb free | NO-GO | Official pricing FAQ: card required at signup — $29 pre-authorisation hold + pro-rated Pro charge; validation up to 3 business days. |
| Hugging Face Spaces (Docker) | NO-GO | 2026 policy change: creating a Gradio or Docker Space requires PRO ($9/mo, payment method). CPU Basic hardware is $0/hr but the *creation gate* is PRO. Static Spaces (no Python server) and ZeroGPU (Gradio only) cannot host this app. |
| Fly.io | NO-GO | $1 free-trial credit, 7 days or until used up; machines stop and cannot restart until a card is added. No permanent free tier for new accounts. |
| Railway | NO-GO | Official status page (2 Nov 2026): new customers must subscribe to a paid plan (Hobby/Pro) before deploying; free-trial deployments unavailable. |
| Vercel | NO-GO | Serverless/functions only — no long-running server. A ThreadingHTTPServer has no Vercel equivalent without a rewrite. |

Sources: https://www.pythonanywhere.com/pricing/,
https://blog.pythonanywhere.com/206/, https://www.koyeb.com/docs/faqs/pricing,
https://huggingface.co/docs/hub/en/spaces-overview,
https://huggingface.co/pricing, https://docs.fly.io/about/free-trial,
https://status.railway.com/incident/O1VGXWU5,
https://help.pythonanywhere.com/pages/RequestingAllowlistAdditions

## What was built (local only — NOT pushed, NOT deployed)

- `notes_bharat/wsgi.py` — WSGI adapter (stdlib only). Same routes as
  the stdlib server (GET /, /api/status, /api/note; POST /api/ask,
  /api/organise, /api/reset-budget), same NotesAgent methods, same
  error mapping. `web.py` untouched. Notes folder resolved from the
  package location unless `NOTES_ROOT` is set (uWSGI workers do not
  start in the repo directory).
- `deployment/pythonanywhere_wsgi.py` — the file the PythonAnywhere
  Web tab points at. Computes the repo path from its own location;
  no username/path is hardcoded.
- `tests/test_wsgi.py` — 7 tests driving the adapter over real HTTP
  (wsgiref): homepage, status (mock), note + missing note (404),
  ask + refusal, ask-without-question (400), organise + reset-budget,
  unknown route (404).
- `deployment/PYTHONANYWHERE_DEPLOY.md` — exact deploy steps.

## Validation (Linux sandbox, Python 3.12.3, 6 Nov 2026)

- Full suite: **39/39 pytest PASS** (32 original + 7 new WSGI tests).
- Stock server smoke: `python3 run.py serve --port 8766` → GET /
  200, GET /api/status 200 (`mode: mock`, 5 notes).
- WSGI smoke (wsgiref + `notes_bharat.wsgi.application`): GET / 200,
  GET /api/status 200 (mock, 5 notes, qwen-3.8-27b), POST /api/ask
  "What is Abhiverse for?" → 200, refused false, `[mock]` label.
- Docker: **not available in this sandbox** (`docker: command not
  found`) — no image was built. Not needed for PythonAnywhere anyway.

## Caveats — read before deploying

- **WSGI files are NOT on GitHub yet.** `notes_bharat/wsgi.py`,
  `deployment/pythonanywhere_wsgi.py`, `tests/test_wsgi.py` and the
  two deploy docs exist only locally. Push them to
  https://github.com/MSAbhishek22/notevault-bharat first (needs the
  user's push approval), or upload the folder via the Files tab.
- **Live mode needs an allowlist request.** PythonAnywhere free
  accounts reach only allowlisted sites. Whether `bharatcode.ai` is
  already allowlisted is **UNVERIFIED**. The deploy ships in mock
  mode (no key, no outbound calls) and works immediately; real mode
  needs the key + a granted allowlist request (request page linked
  in `PYTHONANYWHERE_DEPLOY.md`). Do not claim real mode until a
  real-mode ask succeeds from the live URL.
- **Python 3.12 in the dropdown is unconfirmed** — verify at setup
  (3.13 is also offered in 2026 guides; stdlib-only app, either is
  fine — note which one was picked).
- **1-month expiry:** unused free web apps expire after 1 month and
  need a login + renewal click (email warning first). Not a risk
  for the 10 Nov deadline; diary it anyway.
- **1 web worker** — one request at a time; fine for the demo.

## Next steps (for the parent agent)

1. Push the new files to `MSAbhishek22/notevault-bharat` (user
   approval card required) and verify the new head.
2. Dispatch a browser task: PythonAnywhere account + web-app setup
   exactly per `deployment/PYTHONANYWHERE_DEPLOY.md`. Stop at once
   if any step asks for a card.
3. Verify the live URL (`/`, `/api/status`, ask + refusal) and
   record URL + commit SHA in `deployment/RELEASE_MANIFEST.json`.
4. Record the demo video from the live URL only.
5. Later (after the BharatCode key exists): set the key, request
   the bharatcode.ai allowlist, and only then check real mode.
