# BharatCode Build League — Research record (verified vs unverified)

Checked 2026-11-05 (evening IST). Sources are the official pages unless
stated otherwise. Nothing here is invented; anything not verified is
labelled UNVERIFIED.

## VERIFIED (read on the official pages, 2026-11-05)

### Unstop page
- URL: https://unstop.com/college-fests/bharatcode-build-league-build-with-ai-and-win-rs10000-and-a-rs60000-sde-internship-bharatcodeai-528429/amp
- Event: BharatCode Build League, online, 25 Oct 2026 21:00 IST → 10 Nov 2026 23:59:52 IST.
- Tickets: 0 INR (free entry).
- Prize: winner receives ₹10,000.
- Internship: winner gets an opportunity to interview for a paid SDE
  internship, ₹60,000/month for 3 months (total ₹1,80,000). Winning does
  NOT guarantee the internship — separate interview/selection process.
- Additional (subject to terms): 1,000 GC; 3 complimentary Ginhouse event
  tickets; showcase to BharatCode team/community; consideration for
  selected projects to become official BharatCode offerings; free access
  for eligible students (usage limits); Ginclair learning-path discount.
- What to build: app, AI agent, chatbot, developer tool, automation, or
  any useful product — must use the BharatCode model API. "Focus on
  building something functional that solves a real problem rather than a
  basic demonstration."
- Steps: (1) register on the event page, solo or small team; (2) choose an
  idea; (3) build with the BharatCode model API; (4) publish source in a
  PUBLIC GitHub repo containing `BharatCode.txt` in its root; (5) submit
  the repo link via the official event page with project name + short
  description; (6) evaluation.
- Judging: "community interest and the judges' evaluation. GitHub stars
  and votes submitted through the BharatCode website are among the
  factors considered."
- Eligibility: "open to college students, software developers, AI
  enthusiasts, aspiring founders, and independent builders" — "across
  India" (page intro). No age minimum stated on the page; no India-only
  residency clause in the text fetched.
- Deadline: **10 November 2026 at 11:59 PM IST.**

### bharatcode.ai/hackathon
- URL: https://bharatcode.ai/hackathon
- "Build a standalone product or an integration. It does not have to run
  inside the BharatCode app. Students and other builders are welcome."
- "Register and submit by 10 November 2026 · 11:59 PM IST."
- Judging: "GitHub stars, BharatCode website votes and judges' evaluation."
  Community score = stars + registered-website votes (one vote per
  registered account, changeable); judges' evaluation is separate.
- Per participant: 1,000 free Adaption credits to train a model; winning
  team members get US$1,000 in Adaption credits each + a 30-min workshop
  with an Adaption engineer (timing TBA).
- "Free BharatCode access for students — eligible students can build with
  free student access, subject to the current usage limits."
- "Your entry is tied to your BharatCode account — sign in and you're one
  tap away." Submission: "When your repo is public and BharatCode.txt is
  in the root, submit the GitHub link here."

### bharatcode.ai (homepage)
- URL: https://www.bharatcode.ai/
- "Flat-rate LLM APIs. Built for agents." Live models listed:
  **Qwen 3.8 27B** and **DeepSeek V4.1 Flash** (both "API available",
  queues visible, checked 2026-11-05 23:37 IST).
- Plans: "Students: Qwen free up to 10M tokens a day · Lite ₹299/month."
  "Paid plans have no daily or weekly token allowance… See our fair-use
  policy." Pro offers are manually approved (WhatsApp/Discord/email).
- Chat app at chat.bharatcode.ai; leaderboard of builders by requests.

### BharatCode API shape (from a public Build League entrant)
- Marg — https://github.com/Mqhnish/marg — CLI running on the BharatCode
  model API, created 2026-10-21, 6 stars, MIT, has `BharatCode.txt` in root.
- Its README (read 2026-11-05): key env var `BHARATCODE_API_KEY`; default
  model `qwen-3.8-27b`; Responses API by default, Chat Completions with
  `--api chat`; "BharatCode's API is stateless, so Marg replays the history
  each step with `store: false`"; "Requests that come back `503` (model
  busy) or `429` are retried with backoff"; "Your API key is read from the
  environment only." It also ships guides in 12 Indian languages.
- This app follows the same conventions (key name, default model, Chat
  Completions, 429/503 retry). The Marg README links "BharatCode model
  API" to bharatcode.ai.

### Reuse / prior-work rule
- **No rule forbidding reuse of prior work was found** on either official
  page (Unstop AMP text or bharatcode.ai/hackathon). The pages say "build
  a working project", "build a standalone product or an integration" —
  nothing about fresh-code-only. The re-plumb is therefore treated as
  allowed, and is disclosed honestly in the README and submission draft
  (NoteVault core reused; BharatCode provider, new UI, multilingual
  answers are new). If the full Unstop T&Cs (registration-gated) contain
  a fresh-code clause, that would override this — see UNVERIFIED below.

## RESOLVED 2026-11-06

- **API base URL.** Marg's `marg/llm.py` (`DEFAULT_BASE_URL`, read via the
  GitHub connector 6 Nov 2026) uses `https://bharatcode.ai/api/model/v1`.
  The repo default now matches it (config.py, llm.py); still overridable
  with `BHARATCODE_API_BASE`. Live reachability from this sandbox was NOT
  confirmed (curl to the endpoint timed out) — the first real run with a
  key is the live confirmation.

## UNVERIFIED (do not claim; confirm before the live run)

1. **How a student gets a free API key** (exact signup flow, whether the
   student free tier needs approval, usage limits beyond "10M tokens/day"
   for Qwen). Needs the user's own BharatCode account signup.
2. **Full Unstop T&Cs.** The AMP page text is the complete rules text
   visible without login; any additional terms behind registration
   (team-size cap, fresh-code clause, India-residency proof, age minimum)
   are unverified. Jamao's listing says "1–5 per team" — third-party,
   not official.
4. **Winner-announcement date** — not stated on either official page.
5. **Whether the repo must be created fresh for the league** vs reusing an
   existing repo — not stated (see reuse note above).
6. **Exact free-tier limits** (context/output/queue limits "still apply"
   per bharatcode.ai) — not quantified publicly.

## Design references (Rulebook Gate A — inspected 2026-11-05)

1. **Obsidian graph view** (same category: notes as a network) —
   https://clickup.com/blog/notebook-lm-vs-obsidian/ and
   https://community.obsidian.md/plugins/beautiful-graph (inspected via
   search-result text, not a full page open). Learning: nodes + tag
   clusters make a vault legible at a glance; colour-coded groups and
   folder-lens contours keep clusters readable. Not copied: Obsidian's
   dense force-directed hairball; our constellation is sparse, tag-sector
   laid, with a list fallback.
2. **NotebookLM / Gemini Notebook** (same category: grounded Q&A over
   your sources, with citations) — via the same ClickUp comparison and
   https://www.prezent.ai/blog/notebooklm-alternatives (search-result
   text). Learning: "answers only from your sources + citations" is the
   trust mechanism; upload-and-chat is the interaction. Not copied:
   cloud upload of documents; ours is local-first.
3. **Beautiful Graph (Obsidian plugin)** (exceptional interaction/motion)
   — https://community.obsidian.md/plugins/beautiful-graph (search-result
   text). Learning: distinct visual roles per node type, curated palettes,
   atmosphere that aids navigation. Not copied: desktop-only plugin model.
4. **bharatcode.ai homepage** (product context) — opened in full
   2026-11-05. Learning: flat-rate API framing, live capacity panel,
   leaderboard — the "API is a shared utility" tone. Not copied: its
   marketing layout.
5. **NoteVault (own prior project, local)** — read in full locally
   (design constitution + web.py). Learning: the routing/budget ledger
   works and is worth keeping. Not copied: its visual identity (warm
   off-white ledger, 3-column, system-ui, no hero) — deliberately replaced
   by the night-sky + marigold constellation identity (see registry).
