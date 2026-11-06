# Demo Video Shot List — NoteVault Bharat (record from the LIVE URL only)

**Live URL:** https://notevault-bharat.vercel.app
**Deployment:** Ht1GG5KsLDu1WhSRJMUCGUxU9e8P (Vercel Hobby, Ready 2026-11-06 18:56 IST)
**Commit:** 011c0417fe1e37049739b64cfd3517dacb05a447
**Target:** one continuous take, 60–120 seconds, no cuts, no slides, no screenshots.
**Mode at recording time:** `[mock]` — no BharatCode key is set yet. Say the
mode badge as it appears on screen; never present a mock answer as a live one.
If the key is set before recording, the badge will read `real BharatCode`.

## Setup (before pressing record)

- Real browser (Chrome/Edge/Firefox) on the user's own device, window
  1280×720 or larger, site zoom 100%.
- Open the live URL and wait for the page to finish loading (notes list
  populated, constellation visible) before starting.
- Screen-record the browser window only. No facecam, no narration needed
  (the UI speaks for itself); if narrating, keep it to one line per shot.

## Shots (one take, in order)

| Time | Shot | Live action on screen |
|------|------|-----------------------|
| 0:00–0:10 | Address bar + hero | Live URL visible in the address bar. Homepage shows "NoteVault ✦ Bharat", tagline "Apne notes se poochho, apni bhasha mein", and the `[mock]` mode badge. |
| 0:10–0:25 | Constellation | Drag the 3D constellation to spin it. Click one star — its note opens in the preview pane. |
| 0:25–0:55 | Ask, grounded answer | Click the Ask box, type **"What is Abhiverse for?"**, submit. The answer appears with the `[mock]` label, citations to the note(s), the routing panel (provider/model/why), and the budget meter. |
| 0:55–1:15 | Ask, grounded refusal | Clear the box, type **"quantum bananas"**, submit. The app refuses (grounded refusal — notes do not contain it) and the budget meter does not move. |
| 1:15–1:30 | (Optional) Hinglish | Ask the same Abhiverse question in Hinglish — the answer comes back in Hinglish. Skip if the take is already past 90 s. |
| 1:30–1:45 | Close | Scroll back to the top. End with the hero + live URL on screen. |

## Checks before upload

- [ ] Duration 60–120 s, one continuous take.
- [ ] The live URL is visible in the address bar at the start.
- [ ] At least one real ask with a visible answer, and the refusal.
- [ ] Mode badge visible and honestly shown (`[mock]` until the key is set).
- [ ] No localhost, no screenshots, no slides, no text cards.
- [ ] Upload as Public (or Unlisted, only if the user chooses) and record
      the URL in `DEMO_VIDEO_MANIFEST.md` with `watched_back YES` only
      after actually watching it back.

## Why the sandbox did not record this (2026-11-06 — final)

The sandbox can GET the live site (curl: 200) but its egress blocks
POST responses (control POST to httpbin.org also times out), and the
egress proxy refuses browser connections outright. Chromium was
installed via Playwright (v1.64.1, Chrome for Testing 156) and launches
fine, but every navigation fails (`ERR_TUNNEL_CONNECTION_FAILED` for
HTTPS, `ERR_EMPTY_RESPONSE` for plain HTTP) — with and without proxy
auth, IPv6 literal, `--no-sandbox`, and a curl User-Agent. Direct
egress (no proxy) is blocked too. So the live ask cannot be driven and
no video can be recorded from the sandbox; the recording must happen in
a real browser on the user's device, using the shot list above.
