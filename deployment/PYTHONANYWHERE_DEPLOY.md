# Deploy — PythonAnywhere free tier (card-free)

Status: **NOT DEPLOYED.** Files are ready below; the deploy itself needs
the user's taps (account + web-app setup in the browser). Nothing here
claims a live URL.

Why PythonAnywhere: Render demands a card even for a free-tier deploy
(verified 6 Nov 2026 — new account created, card prompt on deploy).
Koyeb needs a card at signup; Hugging Face Docker Spaces need PRO
($9/mo); Fly.io is a 7-day trial, then a card; Railway needs a paid
plan for new customers; Vercel is serverless and cannot run this
long-lived server. PythonAnywhere's free (Beginner) account needs no
card. Full comparison: `deployment/CARD_FREE_HOST.md`.

## What runs there

The app cannot run as `python3 run.py serve` on PythonAnywhere: free
web apps must be **WSGI** — no port to listen on, no long-lived
server process. The WSGI adapter is `notes_bharat/wsgi.py` (stdlib
only, same routes and same agent as the local server; `web.py` is
untouched). The file PythonAnywhere points at is
`deployment/pythonanywhere_wsgi.py` — it only puts the repo on
`sys.path` and points `NOTES_ROOT` at the repo's notes folder.

## Prerequisites

- A free PythonAnywhere account (Beginner). Signup is email +
  username + password — **no card**. The username chooses the URL:
  `https://<username>.pythonanywhere.com`.
- The code on the server. **Note:** the WSGI files below are local-only
  right now — they are NOT yet on the public repo. Either push them to
  https://github.com/MSAbhishek22/notevault-bharat first (parent's job,
  needs the user's push approval), then `git clone` on the server; or
  upload the whole folder via the Files tab.

## Steps (user's taps — browser)

1. Create the free account at https://www.pythonanywhere.com/
   (Beginner). No card is asked for.
2. Consoles tab → open a Bash console →
   `git clone https://github.com/MSAbhishek22/notevault-bharat.git`
   (github.com is reachable from PA consoles; if git is blocked,
   upload the folder via the Files tab instead).
3. Web tab → **Add a new web app** → **Manual configuration** →
   pick **Python 3.12** (confirm it in the version dropdown; 3.13 is
   also offered in 2026 guides — pick 3.12 if present).
4. Set **Source code** directory to
   `/home/<username>/notevault-bharat`.
5. Set **WSGI configuration file** to
   `/home/<username>/notevault-bharat/deployment/pythonanywhere_wsgi.py`.
6. Click **Reload** (the green button on the Web tab).
7. No environment variables are needed for the first deploy: without
   `BHARATCODE_API_KEY` the app runs in labelled mock mode.

## Verify (after reload)

- `GET https://<username>.pythonanywhere.com/` → 200, page shows
  "NoteVault Bharat" and the mode badge `[mock]`.
- `GET https://<username>.pythonanywhere.com/api/status` → 200,
  `mode` is `mock`, `notes_count` is 5.
- Ask "What is Abhiverse for?" → 200, `refused` false, answer has
  the `[mock]` prefix.
- Ask "quantum bananas" → 200, `refused` true.
- Record the live URL + commit SHA in
  `deployment/RELEASE_MANIFEST.json`, then record the demo video
  from the live URL only (never from localhost/screenshots).

## Live (real BharatCode) mode — LATER, not this deploy

Real `/api/ask` calls need two things, neither of which is done yet:
1. `BHARATCODE_API_KEY` set on the server (Web tab environment
   variables, or `os.environ` in the WSGI file). Never commit it.
2. **bharatcode.ai allowlisted** for free accounts: PythonAnywhere
   free accounts can only reach allowlisted sites over HTTP(S).
   Request it at
   https://help.pythonanywhere.com/pages/RequestingAllowlistAdditions
   (allowlist additions are only granted for sites with an official,
   public, documented API — BharatCode's API is documented at
   https://www.bharatcode.ai/). **Whether bharatcode.ai is already
   allowlisted is UNVERIFIED** — check by running a real-mode ask
   after the key is set. Until the allowlist is granted, real-mode
   calls fail honestly with a provider error; the app never pretends
   a mock answer is real.

## Gotchas (free tier, verified from official pages 6 Nov 2026)

- **1 web worker** — one request at a time. Fine for a demo video
  and judging; do not run load tests against it.
- **No idle sleep** (unlike Render free) — the app stays up; but
  **unused free web apps expire after 1 month** and must be renewed
  by logging in and clicking a button (PythonAnywhere emails a
  warning first). Diary the renewal: the BharatCode deadline is
  10 Nov, so expiry is not a risk for the submission itself.
- **512 MB disk** — the repo + notes are far below this.
- **Python version** — confirm 3.12 is in the Web-tab dropdown at
  setup; if only 3.13 is offered, pick it (stdlib-only app, no
  version-pinned dependency) and note the change here.
