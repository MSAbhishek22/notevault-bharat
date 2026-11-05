# Project Design Registry — NoteVault Bharat (BharatCode Build League)

Comparison vs the three most recent rulebook-era projects, from their
recorded design constitutions (previous project screenshots were not
on file for inspection — noted honestly).

## This project

- Concept: "A constellation over a study desk" — night sky of notes
  above a cream-paper desk; ask in your language, answered by BharatCode.
- Palette: ink navy `#1b2a4a` + marigold `#f0a13a` on cream paper
  `#fdf6e9`; tag stars in six muted hues.
- Type: Georgia serif display + system sans body (Devanagari-capable
  stack). Layout: full-bleed hero → galaxy canvas → 2-column
  (ask+notes | routing+budget).
- Signature interaction: drag-to-spin constellation; click a star to
  open its note; language selector (en/hi/hinglish) changes the answer.
- 3D: canvas perspective-projection note galaxy, tag-sector layout,
  click/arrow-key navigation, reduced-motion static fallback, notes-list
  2D fallback.

## Compared projects

1. **NoteVault (Mozilla Otari, 2026-11-03)** — warm off-white ledger,
   3-column (`1fr / 1.6fr / 1fr`), system-ui throughout, no hero, no 3D,
   Otari routing ledger. DIFFERENCE: Bharat is a night-sky hero +
   galaxy-first layout with serif display type, marigold accent and a
   language selector; nothing ledger-like, no 3-column grid, no Otari.
2. **Digest Room (Flip the Switch, 2026-11-05)** — deep slate
   `#0F1419` + signal lime `#A3E635`, mission-control room, chat
   timeline hero, mono log voice, CSS depth pipeline. DIFFERENCE:
   Bharat is warm cream paper under a navy sky with marigold (not dark
   console + lime), a notes galaxy (not a chat timeline), and serif
   display type (not sans + mono); no room list, no agent log voice.
3. **Spec Ghost (Kiroween, 2026-11-03)** — near-black brown +
   candlelight amber, Georgia serif, 860px single-column candlelit
   document, "a ghost is a question, not a bug". DIFFERENCE: Bharat
   shares Georgia serif but nothing else — it is a bright cream desk
   under a navy sky with a wide hero + galaxy, not a narrow dark
   document; marigold is a star colour, not candlelight; the interaction
   is spinning a constellation, not reading a haunted spec.

Verdict: recognisably different in concept, palette, type, layout,
interaction and motion.
UI_DISTINCTIVENESS: PASS.
