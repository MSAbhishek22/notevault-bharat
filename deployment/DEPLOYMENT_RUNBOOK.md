# Deployment Runbook — NoteVault Bharat

Status: **NOT DEPLOYED. BLOCKED on the user's own taps** (Render account
signup + deploy). Nothing below claims a live URL.

## Stack

- Python 3.12+, **stdlib only** — no dependencies to install at runtime.
- Tests need pytest only (`pip install pytest`).
- Server: `ThreadingHTTPServer`, binds `127.0.0.1` by default.
- Storage: local Markdown files in `notes/` (read-only at runtime; the
  app never writes to the notes folder).

## Environment variables (names only — never values)

| Variable | Purpose | Required? |
|---|---|---|
| `BHARATCODE_API_KEY` | BharatCode model API key (from your BharatCode account) | Only for live mode; mock demo works without it |
| `BHARATCODE_API_BASE` | API base URL (default `https://api.bharatcode.ai/v1` — **UNVERIFIED**, confirm in your BharatCode account) | No (has default) |
| `BHARATCODE_MODEL` | Default model id (default `qwen-3.8-27b`) | No |
| `BHARATCODE_FALLBACK_MODEL` | Fallback model id (default `deepseek-v4.1-flash`) | No |
| `BHARATCODE_PROVIDER` | `auto` / `mock` / `bharatcode` | No |
| `BHARATCODE_LANGUAGE` | `en` / `hi` / `hinglish` | No |
| `NOTES_ROOT` | Notes folder (default `notes`) | No |
| `PORT` | Render sets this; the app reads `--port` | Render only |

## Deploy target (planned, not done): Render free tier

Why Render: free web service, Python stdlib app, no build step, no
database. Stop at once if any step asks for a card.

Planned steps (user's taps — NOT done by this agent):

1. Create the public GitHub repo (e.g. `MSAbhishek22/notevault-bharat`)
   and push this folder. Verify `BharatCode.txt` is at the repo root.
2. Sign up / sign in to Render (free), New → Web Service → connect the
   repo. **Stop if a card is asked.**
3. Settings: Runtime Python 3; Build Command: (none — stdlib only);
   Start Command: `python3 run.py serve --host 0.0.0.0 --port $PORT`.
   Note: the app binds localhost by default; Render needs `0.0.0.0`
   + `$PORT` — that is the only host change, and it is Render's
   documented pattern for web services.
4. Environment: set `BHARATCODE_API_KEY` (from your BharatCode account)
   in Render's environment settings. Do NOT commit it.
5. Deploy, then open the live `.onrender.com` URL in a fresh browser:
   load `/`, check the mode badge says `real BharatCode`, ask a
   question, check the routing panel + budget, click a galaxy star,
   check mobile width. Record the URL + commit SHA in
   `deployment/RELEASE_MANIFEST.json`.
6. Free-tier note: Render free services sleep after inactivity
   (~15 min) with a ~60s cold start. That is acceptable for judging
   if the URL is warmed before the demo video is recorded.

## Health checks (after deploy)

- `GET /` → 200, page contains "NoteVault Bharat" and "galaxy".
- `GET /api/status` → 200, `mode` is `real-bharatcode`, `notes_count` ≥ 1.
- `POST /api/ask {"question": "What is Abhiverse for?"}` → 200,
  `refused` false, answer has no `[mock]` prefix.
- `POST /api/ask {"question": "quantum bananas"}` → 200, `refused` true.

## Rollback

Render keeps prior deploys: redeploy the previous commit from the
Render dashboard, or `git revert` + push. No database, no migrations —
rollback is a redeploy.

## Ownership

Owner: M S Abhishek. Repo: to be created (planned
`MSAbhishek22/notevault-bharat`). Production branch: `main`.
