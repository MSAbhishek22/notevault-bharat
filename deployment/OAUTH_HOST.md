# Password-free host for NoteVault Bharat — findings

**Date:** Fri 6 Nov 2026. **Verdict: Vercel Hobby is the GO.**
PythonAnywhere stays the preferred host if the user ever sets its
account password, but it is blocked on that password alone. Vercel
signs up with GitHub OAuth — no password, no card — and the app now
has a Vercel entrypoint built and tested. Research was read-only
(public web + official docs); nothing was created, signed into, or
paid for.

## Ranking

| Host | Verdict | Why (evidence) |
|---|---|---|
| **Vercel Hobby (Python Functions)** | **GO** | GitHub OAuth signup, no Vercel password, no card for Hobby (accounts doc: "sign up with… GitHub, GitLab, Bitbucket"; Hobby doc: "The Hobby plan is free… there are no billing cycles"; card details appear only in upgrade steps). Python 3.12 is the default. Single WSGI function, 300 s Hobby timeout. No idle sleep — serverless, scales to zero, cold start on request. Live URL `<project>.vercel.app`. |
| **Replit (1 free published app)** | **GO, temporary** | GitHub/Google OAuth signup, no card (docs: Starter "free with no time limit", 1 free published app). Run `python3 run.py serve`; live `*.replit.app` URL. But: sleeps after 15 idle minutes, and **the link expires after 30 days** and must be re-published. Caution: the free Starter plan no longer appears on replit.com/pricing (removed ~11 Sep 2026) though billing docs still describe it — confirm at signup. |
| **Cloudflare Workers (Python)** | **Backup, signup unverified** | Python via Pyodide, WSGI supported (Flask guide, Sep 2026), free tier 100k req/day, no card per secondary sources. But GitHub/Google OAuth signup could NOT be verified — evidence points to email signup. Needs a live-browser check of the signup screen before it counts as password-free. |
| Glitch | DEAD | Hosting ended 8 Jul 2025 (official blog, 22 May 2025); glitch.com now resolves to the blog only. |
| Northflank Sandbox | NO-GO | Only always-on free option, but billing docs: "All users must add a payment method to start creating resources, regardless of plan" — contradicts the pricing page's "No card needed". |
| Zeabur | NO-GO | No new free compute: shared cluster stopped accepting new projects 15 Mar 2026. |
| Sevalla (ex-Kinsta) | NO-GO | "A payment method is required at signup"; no free app tier. |
| Netlify Functions | NO-GO | No Python runtime (JS/TS only). |
| Hugging Face Spaces | NO-GO | Gradio/Docker Spaces need PRO ($9/mo) to create (confirmed in docs). |
| Alwaysdata | NO-GO | Free, no card, Python WSGI — but signup is email + password, fails the no-password rule. |
| Streamlit Cloud | NO-GO | Streamlit apps only. |
| Deno Deploy | NO-GO | JS/TS only; shutting down ~Apr 2027. |
| Render / Koyeb / Railway / Fly.io | NO-GO | Already ruled out (card on deploy / card at signup / paid plan / card). See deployment/CARD_FREE_HOST.md. |

Sources: https://vercel.com/docs/accounts/create-an-account,
https://vercel.com/docs/plans/hobby,
https://vercel.com/docs/functions/runtimes/python,
https://vercel.com/docs/functions/runtimes/python/api-directory,
https://vercel.com/pricing, https://docs.replit.com/help/pricing-and-plans,
https://docs.replit.com/billing/deployment-pricing,
https://docs.replit.com/billing/plans/starter-plan,
https://developers.cloudflare.com/workers/languages/python/,
https://blog.glitch.com/post/changes-are-coming-to-glitch,
https://northflank.com/pricing, https://zeabur.com/changelogs/phasing-out-shared-cluster,
https://www.alwaysdata.com/en/register/, https://streamlit.io/cloud,
https://deno.com/deploy

## What was built for Vercel (local only — NOT pushed, NOT deployed)

- `pyproject.toml` — `[tool.vercel] entrypoint =
  "notes_bharat.wsgi:application"`: the Python runtime loads the WSGI
  app from that module and routes EVERY request to it with the original
  path, so the app deploys as-is. No `api/index.py` shim and no
  `vercel.json` rewrite: a rewrite to `/api/index` used to mask every
  path as PATH_INFO=/api/index and made the live app 404 on `/`,
  `/api/status` and everything else (first deploy, 6 Nov 18:46 IST).
  The fix and the full diagnosis are in
  `deployment/VERCEL_ROUTING_FIX.md`. `vercel.json` is now `{}` (no
  custom routing).
- `tests/test_vercel_entrypoint.py` — 7 tests: entrypoint declared and
  resolvable, no rewrites in vercel.json, no `api/index.py` shim left,
  homepage, status (mock, 5 notes), ask + refusal driven over real
  HTTP via wsgiref against the repo's real notes folder.
- `tests/test_vercel_routing_regression.py` — 4 regression tests:
  the old rewrite reproduced locally (PATH_INFO forced to /api/index
  → 404 on / and /api/status), the entrypoint serving original paths,
  ask + refusal, and a direct GET /api/index answering the app's own
  404 without breaking later routing.

## Validation (Linux sandbox, Python 3.12.3, 6 Nov 2026)

- Full suite: **50/50 pytest PASS** (44 before the routing fix + 6
  new/rewritten Vercel tests, 6 Nov 2026, Linux sandbox Python 3.12.3).
- `vercel.json` parses (now `{}` — no rewrites); the entrypoint
  declared in `pyproject.toml` resolves to the callable
  `notes_bharat.wsgi.application` (checked directly).
- **Routing fix NOT yet deployed:** the live deployment
  (EoWHmRM7qNxjyenGTFiHQRyhVq7P, 6 Nov 18:46 IST) still runs the old
  rewrite build and 404s on every path. Push the fix and verify the
  auto-deploy before calling the URL live.

## Honest behaviour differences vs the local server

- **Budget counter is demo-only on Vercel.** It lives in memory on
  the agent built at import. It persists while an instance is warm,
  but resets on every cold start and can diverge across concurrent
  warm instances. `/api/reset-budget` and the meter still work
  per-instance. Durable counting would need a backing store — not
  built. Label it as session/ephemeral, never as a global budget.
- **Cold starts.** First request after idle (or after a function is
  archived, ~2 weeks without invokes) pays at least ~1 s extra.
  No Render-style sleep takes the site offline; the deployment
  stays live.
- **Read-only filesystem is fine.** The app never writes in the
  serving path (only the CLI's optional `--write` does); notes are
  bundled and read via `__file__`-based absolute paths.
- **Mock mode is unchanged.** No key needed for the first deploy;
  every answer is labelled `[mock]`, exactly as locally.
- **Real mode is easier here than on PythonAnywhere:** Vercel has
  no outbound allowlist, so real BharatCode mode later needs only
  the `BHARATCODE_API_KEY` env var — no allowlist request.
- **Hobby limits** (ample for a demo): 1M function invocations/mo,
  100 GB transfer/mo, 4 hrs Fluid Active CPU/mo. Hobby is
  non-commercial personal use — fits a hackathon demo.
- **Possible signup friction (unverified for India):** Vercel
  community reports some GitHub signups are asked for SMS/phone
  verification. Not a card gate; if it appears, stop and report.

## Next steps (for the parent agent)

1. Push the fix to `MSAbhishek22/notevault-bharat` (user approval
   card required): `pyproject.toml` (entrypoint), `vercel.json` (no
   rewrites), `tests/test_vercel_entrypoint.py`,
   `tests/test_vercel_routing_regression.py`,
   `deployment/VERCEL_ROUTING_FIX.md`. **Snapshot pushes do NOT
   delete files, so `api/index.py` will still be on the remote after
   the push — delete it on GitHub (web UI) in the same step, or the
   stale /api/index function stays deployed alongside the entrypoint.**
   Verify the new head.
2. Dispatch a browser task: Vercel signup via "Continue with
   GitHub" (MSAbhishek22, already signed in), Hobby plan, import
   repo `MSAbhishek22/notevault-bharat`, deploy (no build command,
   no env vars). **Stop at once if a card is asked; stop and
   report if phone/SMS verification appears.** Expected URL:
   `https://notevault-bharat.vercel.app` (or the generated name).
3. Verify the live URL (`/`, `/api/status` mock + 5 notes, ask +
   refusal) and record URL + commit SHA in
   `deployment/RELEASE_MANIFEST.json`.
4. Record the demo video from the live URL only.
5. PythonAnywhere remains the fallback if the user ever sets its
   password (WSGI adapter already built + pushed at `b4eff38`).
   Replit is the second fallback (30-day link expiry); Cloudflare
   Workers only after its signup screen is checked in the browser.
