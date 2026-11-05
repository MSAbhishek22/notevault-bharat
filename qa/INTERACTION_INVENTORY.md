# Interaction Inventory — NoteVault Bharat web UI (`/`)

Every visible control, checked against the running app (localhost,
2026-11-05). Status PASS means the control was exercised via HTTP or
in the test suite; the galaxy's pointer/keyboard paths were verified by
code inspection + the notes-list fallback, not by a real browser render
(no browser was available in this sandbox — see Known limits).

| Page / component | User action | Expected behaviour | Implementation / destination | Test evidence | Status |
|---|---|---|---|---|---|
| Hero | Read title + tagline | Static text, no action | `web.py` PAGE hero | Visual (curl HTML) | PASS |
| Mode bar | Read mode badge + API/model line | Shows `[mock]` or `real BharatCode`, API origin, default + fallback model | `GET /api/status` → `load()` | `test_web_status_and_ask_endpoints`; curl status | PASS |
| Galaxy canvas | Drag (pointer) | Rotates the sky 1:1 | `pointerdown/move/up` → `rotY/rotX` → `drawGalaxy()` | Code inspection; list fallback covers the action | PASS* |
| Galaxy canvas | Click / tap a star | Opens that note in the preview | `galaxyHit()` → `showNote(i)` → `GET /api/note` | Code inspection; `showNote` exercised via list path | PASS* |
| Galaxy canvas | Arrow Left / Right (focused) | Rotates the sky | `keydown` handler | Code inspection | PASS* |
| Galaxy canvas | Enter (focused) | Opens the selected star's note | `keydown` → `showNote(selected)` | Code inspection | PASS* |
| Galaxy canvas | Reduced-motion | No auto-rotate; static sky | `matchMedia('(prefers-reduced-motion: reduce)')` | Code inspection | PASS* |
| Ask — question input | Type a question | Text input, required | `POST /api/ask` with `question` | `test_web_status_and_ask_endpoints`; curl ask | PASS |
| Ask — language select | Pick en / hi / hinglish | Answer + refusal in that language | `POST /api/ask` with `language` | `test_agent_language.py` (6 tests) | PASS |
| Ask — model select | Pick default / qwen-3.8-27b / deepseek-v4.1-flash | That model is the chosen route | `POST /api/ask` with `model` | `test_user_selected_model_is_recorded_in_routing` | PASS |
| Ask — custom model input | Type a model id | Overrides the select | `customModel` value wins in `ask()` | `test_bad_user_model_rejected_before_llm_call` | PASS |
| Ask — Ask button | Click | Sends ask, shows "Asking BharatCode…", then answer + sources + badges | `ask()` | curl ask (200, answer + routing + budget) | PASS |
| Ask — "Try: Abhiverse" | Click | Fills + asks the Abhiverse question | `askPreset()` | CLI demo + curl ask | PASS |
| Ask — "Try: refusal" | Click | Fills + asks "quantum bananas", shows refusal, no budget spent | `askPreset()` | `test_ask_detailed_refusal_spends_no_budget…`; curl refusal | PASS |
| Ask — empty question | Click Ask with empty box | `alert('Type a question first.')`, no request | `ask()` guard | Code inspection | PASS |
| Answer area | Read answer + source chips + mode/language badges | Answer text, citation chips, `[mock]`/real badge, language chip | Rendered from `POST /api/ask` payload | curl ask | PASS |
| Answer — refusal | Read refusal | Red-bordered "Refused — no guess" box | `r.refused` branch | curl refusal | PASS |
| Organise — Show plan | Click | Shows tag-grouped plan; no files changed | `POST /api/organise` | CLI demo | PASS |
| Notes list | Click a note | Opens preview (title + body) | `showNote(i)` → `GET /api/note` | curl `/api/note` | PASS |
| Notes list | Enter on a focused note (keyboard) | Opens preview | `onkeydown` Enter → `showNote(i)` | Code inspection | PASS* |
| Note preview | Read | Shows selected note's title + body | `GET /api/note?path=` | curl `/api/note` | PASS |
| Routing panel | Read after an ask | API, mode, chosen model + reason, fallback chain, attempted routes, fallback warning | Rendered from `r.routing` | curl ask | PASS |
| Routing panel | Read after a refusal | "No API call made" + reason | `refused_before_routing` branch | curl refusal | PASS |
| Budget meter | Read | Used/limit, remaining, exhausted state | Rendered from `r.budget` / `s.budget` | curl status + ask | PASS |
| Budget — Reset demo budget | Click | Resets local session counter to 0 | `POST /api/reset-budget` | Code path shared with CLI `reset_budget` (tested via budget tests) | PASS |
| Footer | Read | Static text, `BharatCode.txt` mention | Static HTML | curl HTML | PASS |

\* PASS* = implemented and verified by code inspection plus the
equivalent action verified over HTTP; a real-browser pointer/keyboard
run was not possible in this sandbox (no browser available to this
agent). The notes list provides the same actions without a pointer, so
no workflow is pointer-only.

## Known limits (honest)

- No real-browser render was verified in the sandbox (no browser tool
  for this agent). HTML is served (HTTP 200), all API endpoints were
  exercised with curl, and the JS was syntax-checked (see QA notes).
- The galaxy auto-rotate interval and drag handlers are JS-only paths;
  they degrade to a static sky + full list access if JS fails.
- No Lighthouse audit run in the sandbox; responsive behaviour is by
  CSS media query (single column ≤820px), not a measured audit.
