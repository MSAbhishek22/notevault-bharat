# NoteVault Bharat ✦ — Apne notes se poochho, apni bhasha mein.

**Ask your own notes, in your language — answered by the BharatCode model API.**

Built for the **BharatCode Build League** (deadline **10 Nov 2026, 11:59 PM IST**).
Solo entry by M S Abhishek ([@MSAbhishek22](https://github.com/MSAbhishek22)).

Your notes stay on your machine. Only the few excerpts that match your
question go to BharatCode — and only when you ask. Answers are grounded:
if your notes don't have it, the app refuses instead of guessing, and
every answer cites the notes it used.

## What makes it BharatCode-native

- **Real BharatCode model API** — Chat Completions, `qwen-3.8-27b` by
  default, `deepseek-v4.1-flash` as fallback, with 429/503 retry + backoff
  (the behaviour documented by the public Build League entrant
  [Marg](https://github.com/Mqhnish/marg)). Key from `BHARATCODE_API_KEY`
  only — never in the repo, never logged.
- **Answer in your language** — English, हिन्दी (Devanagari) or Hinglish.
  The language is your choice, not the model's default.
- **Routing you can see** — every answer shows the API, the model, why it
  was chosen, the fallback chain, and which routes were actually attempted.
- **Budget you can see** — local session meter (5 calls/run by default).
  BharatCode-side usage lives in your BharatCode account (students: Qwen
  free up to 10M tokens a day, per bharatcode.ai) — the app never invents
  a gateway number.
- **Note constellation (3D)** — your notes as stars, tags as constellations.
  Drag to spin the sky, click a star to read its note. The plain notes list
  is the always-available 2D fallback; everything works from the keyboard.
- **Grounded refusal** — no matching notes means no API call, no budget
  spent, and an honest refusal in your language.

## Run it (no key needed for the mock demo)

```bash
python3 run.py serve
# open http://127.0.0.1:8769/
# try: "What is Abhiverse for?" then "quantum bananas" (refusal)
# try the same question in Hinglish, and spin the constellation
```

CLI still works:

```bash
python3 run.py index
python3 run.py ask "What is Abhiverse for?"
python3 run.py ask "Abhiverse kya hai?" --lang hinglish
python3 run.py summarise study-python.md
python3 run.py organise
python3 run.py demo
python3 run.py status
```

## Go live with BharatCode (your taps)

```bash
export BHARATCODE_API_KEY="<redacted>"   # from your BharatCode account
python3 run.py serve
```

If your BharatCode account shows a different API base URL than the
default in `.env.example`, set `BHARATCODE_API_BASE` — the default
(`https://bharatcode.ai/api/model/v1`) is verified from the public
entrant Marg's client, see `RESEARCH.md`.

## Tests

```bash
pip install pytest
python3 -m pytest tests/ -q
# 39 passed (Linux, 2026-11-06 — 32 original + 7 WSGI tests) — no network, no key needed
```

## Honest status (Rulebook gates)

| Gate | Status |
|---|---|
| A Research + design | PASS (design docs in `design/`) |
| B Functional product | PASS (32/32 tests, HTTP-verified locally) |
| C 3D + visual quality | PASS (constellation + fallbacks, see design docs) |
| D QA | PASS (tests + interaction inventory in `qa/`) |
| E GitHub + deployment | **BLOCKED** — no repo yet, no live deploy (needs your taps) |
| F Demo video | **BLOCKED** — video only ever from a live URL, after deploy |
| G Final handoff | IN PROGRESS — submission draft in `submission/` |

**Overall: IN_PROGRESS, not COMPLETE.** No live URL, no video, no
submission yet — those need the user's own taps (repo creation, Render
deploy, video recording, Unstop + BharatCode submission).

## Where it came from

Re-plumbed from NoteVault (Mozilla Otari track, built 2026-11-03): the
local search, guardrails, routing and budget core is reused; the Otari
provider is replaced by a BharatCode provider, the UI is a new identity
(ink-navy night sky + marigold, hero + constellation), and multilingual
answers are new. No BharatCode rule forbidding reuse of prior work was
found on the official pages — see `RESEARCH.md` for the exact verified
vs unverified list.

## Files

- `notes_bharat/` — the app (stdlib only): `config`, `llm` (BharatCode +
  mock), `routing`, `agent`, `index`, `guardrails`, `cli`, `web`
- `notes/` — sample notes (incl. a BharatCode League fact sheet)
- `tests/` — 32 tests, no network
- `design/` — constitution, design registry, references
- `qa/` — interaction inventory
- `deployment/` — runbook + release manifest (deploy BLOCKED)
- `submission/` — submission draft + video manifest (video BLOCKED)
- `BharatCode.txt` — required Build League file, repo root
- `RESEARCH.md` — verified vs unverified facts + sources
