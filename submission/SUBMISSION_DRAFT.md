# Submission draft — BharatCode Build League (DO NOT SUBMIT YET)

Status: **DRAFT ONLY. Nothing here has been registered, submitted or
posted.** Submission needs the user's own taps (Unstop registration,
BharatCode account + key, GitHub repo, Render deploy, video, then the
submit forms). Deadline: **Tue 10 Nov 2026, 23:59 IST**.

## Where to submit (two places — both are the user's taps)

1. **Unstop** — https://unstop.com/college-fests/bharatcode-build-league-build-with-ai-and-win-rs10000-and-a-rs60000-sde-internship-bharatcodeai-528429/amp
   Register for the event, then submit the repo link + project name +
   short description through the official event page.
2. **bharatcode.ai/hackathon** — https://bharatcode.ai/hackathon —
   "When your repo is public and BharatCode.txt is in the root, submit
   the GitHub link here." (Entry is tied to the BharatCode account.)

## Project name

**NoteVault Bharat** — "Apne notes se poochho, apni bhasha mein."

## Short description (for the forms)

Ask your own notes, in your language — answered by the BharatCode model
API. NoteVault Bharat is a local-first notes assistant: your Markdown
notes stay on your machine, only the excerpts matching your question go
to BharatCode (Qwen 3.8 27B, DeepSeek V4.1 Flash fallback), and answers
are grounded — if your notes don't have it, it refuses instead of
guessing, with citations. Answers come in English, Hindi or Hinglish.
Every answer shows its route (API, model, why, fallback chain, attempts)
and its budget. A 3D note constellation maps the vault: notes are stars,
tags are constellations — drag to spin, click a star to read its note.

## Links (fill in after the user taps)

- GitHub repo: (to be created — planned https://github.com/MSAbhishek22/notevault-bharat)
- Live demo URL: (pending Render deploy)
- Demo video: (pending — recorded ONLY from the live URL, after deploy)

## Honest reuse disclosure (include in the repo README — already there)

Re-plumbed from NoteVault (Mozilla Otari track, built 2026-11-03): the
local search, guardrails, routing and budget core is reused; the Otari
provider is replaced by a BharatCode provider, the UI is a new identity
(ink-navy night sky + marigold, hero + constellation), and multilingual
answers are new. No rule forbidding reuse of prior work was found on the
official pages — see RESEARCH.md.

## Pre-submit checklist

- [ ] Unstop registration done (user's tap)
- [ ] BharatCode account created; free student API key obtained (user's tap)
- [ ] API base URL confirmed in the BharatCode account; `BHARATCODE_API_BASE` set if different
- [ ] Public GitHub repo created + pushed; `BharatCode.txt` verified at root
- [ ] Render free deploy live; production smoke test passed (see runbook)
- [ ] Live run verified: mode badge says `real BharatCode`, no `[mock]` in answers
- [ ] Demo video recorded from the LIVE URL (60–120s), manifest filled in
- [ ] Repo link submitted on Unstop + bharatcode.ai/hackathon (user's taps)
- [ ] Stars/votes: share the repo + BharatCode project page (no fake engagement)

## Judging factors (per official pages)

GitHub stars + BharatCode website votes + judges' evaluation. Stars and
votes are community interest — they are earned after submission, not
before; nothing here claims any.
