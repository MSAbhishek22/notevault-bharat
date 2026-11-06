# Demo Video Manifest — NoteVault Bharat

Status: **LIVE URL READY — video NOT yet recorded.** The production
URL below is verified live (GET / 200, /api/status 200, mock mode, 5
notes). Per the Rulebook and the user's standing rule, a submission
video is recorded ONLY from the verified production URL, never from
screenshots or a localhost recording.

- Production URL: https://notevault-bharat.vercel.app
- Release version: 0.1.0
- Deployed commit SHA: 011c0417fe1e37049739b64cfd3517dacb05a447
- Deployment ID: Ht1GG5KsLDu1WhSRJMUCGUxU9e8P (Vercel Hobby, Ready 2026-11-06 18:56 IST)
- Recording date: (pending)
- Duration target: 60–120s
- Video file: (pending — ~/workspace/hackathons/bharatcode/submission/notevault-bharat-demo.mp4 when recorded)
- Published URL: (pending — upload only after user approves visibility + metadata)

## Blocker (2026-11-06, sandbox — final)

The sandbox can GET the live site (curl: 200) but its egress blocks
POST responses (control POST to httpbin.org also times out), and the
egress proxy refuses browser connections outright: Chromium was
installed via Playwright (v1.64.1, Chrome for Testing 156) and launches
fine, but every navigation fails — `ERR_TUNNEL_CONNECTION_FAILED` for
HTTPS, `ERR_EMPTY_RESPONSE` for plain HTTP — with and without proxy
auth, IPv6 literal, `--no-sandbox`, and a curl User-Agent. Direct
egress (no proxy) is blocked too. So no video can be recorded from the
sandbox. Record it in a real browser from the live URL instead — see
DEMO_VIDEO_SHOT_LIST.md.

## Planned shot list (for the live recording, once deployed)

1. Live URL in the address bar; hero + "Apne notes se poochho" tagline.
2. Spin the constellation; click a star; the note opens in the preview.
3. Ask "What is Abhiverse for?" in English — answer + citations +
   routing panel + budget meter visible.
4. Ask the same in Hinglish — answer in Hinglish.
5. Ask "quantum bananas" — grounded refusal, no budget spent.
6. Show the mode badge: currently `[mock]` (no BharatCode key yet).
   If the key is set before recording, show `real BharatCode` instead
   and say so on screen — never present a mock answer as a live one.
7. Close: repo + live URL on screen.
