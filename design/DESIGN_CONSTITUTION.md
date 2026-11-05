# NoteVault Bharat — Design Constitution

> Written 2026-11-05 as a Rulebook Gate A document, from the UI as it
> actually exists in `notes_bharat/web.py` (single-page HTML, inline CSS,
> canvas galaxy, no external assets, no CDN, no custom fonts). Nothing in this file claims a design that is
> not in the code. Where the current UI falls short of the Rulebook, that
> is stated as a gap, not papered over.

## Product personality and emotional tone

A study desk at dusk in India: calm, warm, a little proud. The product's
promise is "apne notes se poochho, apni bhasha mein" — ask your notes in
your language. Tone in copy: plain, factual, warm where it costs nothing
("Apne notes se poochho"), never hype. The mock badge is deliberately
loud (amber) so a mock answer can never be mistaken for a live one.

## Target user, environment, context of use

A solo Indian student / developer with a local folder of Markdown notes,
working on a laptop browser. The judge/demo viewer is the primary
audience: they must be able to see, in one screen, the constellation,
the answer, the routing decision, and the budget. The CLI is the
secondary surface (same agent, same rules).

## Visual metaphor / central design idea

**A constellation over a study desk.** The night sky (ink navy) holds
your notes as stars; stars sharing a tag form a constellation. The ask
panel below is the desk — cream paper, ink text, marigold accents. The
galaxy is not decoration: it is the spatial map of the vault (which
notes exist, how they cluster by tag), and clicking a star opens the
note. The routing panel is the audit trail under the desk lamp.

## Colour palette (semantic roles, from `web.py` — exact values)

| Role | Value | Used for |
|---|---|---|
| Night sky / hero | `#101a30` → `#1b2a4a` gradient | Hero, galaxy canvas |
| Hero text | `#fdf6e9` (cream) | Hero headings |
| Hero secondary | `#e8e0cc` | Hero body |
| Marigold accent | `#f0a13a` | Stars, highlights, Hindi tagline, meter fill |
| Marigold deep | `#d98200` | Budget meter fill |
| Paper background | `#fdf6e9` (cream) | Page |
| Card | `#fffdf6`, border `#e5dcc4`, radius `16px` | Ask / notes / routing cards |
| Ink text | `#1e2430` | Body text |
| Muted text | `#5c6470` | Small print, footnotes |
| Primary button | `#1b2a4a` bg, `#fff` text, radius `10px` | Ask |
| Secondary button | `#fff` bg, `#1b2a4a` text | Presets |
| Mock badge | bg `#ffe8c2`, text `#7a3e00` | `[mock]` |
| Real badge | bg `#dcefd8`, text `#145214` | `real BharatCode` |
| Citation chip | bg `#fdeecf`, border `#ecd9a8` | Source note titles |
| Refusal / error | border `#b00020`, bg `#fff0f0` | Grounded refusal, API errors |
| Answer / plan block | bg `#f7efdb` | Answer text, organise plan |
| Tag star colours | `#f0a13a`, `#7fd1c0`, `#e78fb3`, `#a5d6a7`, `#90caf9`, `#ffcc80` | One per tag (hash-assigned) |

No gradients except the hero sky, no glassmorphism, no glow, no floating
blobs. The restraint is intentional and matches the desk metaphor.

## Typography and type hierarchy

- **Display:** Georgia serif for the title and card headings — a
  bookish, desk-like voice. (Google Fonts "Fraunces" was considered and
  rejected: no external dependency for the headline; Georgia is on every
  machine.)
- **Body/UI:** `system-ui, -apple-system, "Segoe UI", Roboto, "Noto Sans",
  sans-serif` — Noto Sans in the stack so Devanagari (हिन्दी) renders
  correctly on systems that have it.
- **Hierarchy:** hero `h1` 2.1em serif → card `h3` serif → body → `small`
  muted footnotes. Answer and plan text is rendered in `<pre>` with
  wrapping, inherited font (not monospace — answers are prose, and Hindi
  in monospace renders poorly).
- Gap vs Rulebook: no loaded web font, so the type system is
  size/weight/serif-vs-sans only. Accepted: the product is a tool, and
  offline rendering matters more than a display face.

## Layout grid, spacing, composition

- Page: `max-width: 1080px`, centred, hero full-bleed above.
- Hero: centred, 34px top padding, title + Hindi tagline + one-paragraph
  pitch. This is the entry experience NoteVault lacked.
- Galaxy card: full-width, 300px canvas, night-sky background, rounded
  16px. Below it, a two-column grid (`1.5fr / 1fr`): Ask + Notes on the
  left, Routing + Budget on the right. Mobile (`≤820px`): single column.
- No sidebar, no navigation bar: the page is a single route (`/`), and
  that is the whole product surface.

## Navigation and information architecture

- One route: `/`. Information architecture is hero → constellation →
  ask → notes → routing/budget. The mode bar (`[mock]` badge + API/model
  line) sits between hero and galaxy.
- API routes (not navigation): `GET /`, `GET /api/status`,
  `GET /api/note?path=`, `POST /api/ask`, `POST /api/organise`,
  `POST /api/reset-budget`.

## Component behaviour and interaction patterns

- Ask: question input + language select (en/hi/hinglish) + model select
  (default / qwen-3.8-27b / deepseek-v4.1-flash / custom id) + Ask button
  + two preset buttons (Abhiverse, refusal demo). Asking shows
  "Asking BharatCode…" then the answer, source chips, mode badge and
  language chip. Refusal renders a red-bordered "Refused — no guess" box.
- Galaxy: pointer drag rotates (Y + slight X, clamped ±0.6 rad); click /
  tap a star opens its note in the preview; arrow keys rotate when the
  canvas is focused; Enter opens the selected star; auto-rotate every
  50ms (+0.004 rad) unless `prefers-reduced-motion` — then static.
- Notes list: click or Enter opens the preview; hover highlights.
  This list is the 2D fallback for the galaxy — every galaxy action is
  doable here.
- Routing panel: API, mode label, chosen model + reason, fallback chain,
  attempted routes, fallback-used warning, or "No API call made" on
  refusal. Budget: meter + used/limit + exhausted state + reset button.
- All buttons have `:focus-visible` marigold outlines; all inputs have
  labels; the canvas has an `aria-label` describing keyboard use.

## Motion language

Slow, celestial, restrained: the sky drifts (auto-rotate), stars do not
twinkle, nothing bounces. Drag rotation is 1:1 with the pointer. Motion
communicates "this is a sky you can turn", nothing else. Reduced-motion
users get a static sky with full list access.

## 3D concept and its connection to the product's purpose

The constellation is the vault's map. A flat list hides structure; the
galaxy shows it: how many notes, which tags dominate, which notes sit
alone. Tag sectors (deterministic hash of the tag → angle) mean the same
vault always renders the same sky, so a returning user can read it.
Implementation: canvas 2D with a perspective projection (focal length
420), no dependency, no WebGL — the data is small and the effect is
depth, not a model viewer. Fallbacks: reduced-motion → static render;
no canvas / no pointer → the notes list below (always rendered).
Performance: ≤ a few hundred notes is trivial; the draw is one pass
over projected points. Keyboard alternative: arrow keys + Enter, plus
the fully keyboard-accessible list.

## Responsive behaviour

- Desktop: hero + galaxy + two-column grid.
- Tablet/mobile (`≤820px`): single column; galaxy canvas scales to
  container width (1000×300 internal resolution, CSS width 100%).
  Touch: pointer events handle drag + tap on the canvas.
- No horizontal overflow: the grid collapses, inputs are 100% width,
  `pre` wraps.

## Accessibility and reduced-motion behaviour

- `prefers-reduced-motion: reduce` → auto-rotate off, static sky.
- Focus visible everywhere (marigold outline). Labels on every input.
- Canvas has `tabindex="0"` + `aria-label` with keyboard instructions.
- Colour is never the only signal: the mock badge has text, the
  fallback warning has text, selected star has a white ring + a text
  line naming the selected note.
- Contrast: ink on cream and cream on ink-navy both pass at body sizes;
  muted `#5c6470` on cream is used only for small print.

## Reference links and original design decisions

- References: see `design/DESIGN_REFERENCES.md` (Obsidian graph view,
  NotebookLM, Beautiful Graph, bharatcode.ai, NoteVault).
- Original decisions: night-sky + marigold (not NoteVault's ledger, not
  Digest Room's slate+lime, not Spec Ghost's candlelit serif document);
  hero + galaxy-first layout (not a 3-column ledger); serif display type
  (NoteVault used system-ui everywhere); Hindi/Hinglish as a first-class
  UI choice, not an afterthought.
