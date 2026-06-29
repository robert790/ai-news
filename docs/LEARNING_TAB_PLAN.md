# Learning Tab → In-App Course · Research Report
*Generated: 2026-06-29 · Sources: 18 web sources + 1 deep-read (Duolingo breakdown) · Confidence: High*

## User intent (verbatim, RO+EN)
> "cum sa trecem direct la jobs? nu vezi ca nu e complet nimic in Learning, nu vrea sa ne scoata din OpenRadar, vrem sa fie totul afisat acolo! ... schema aia nu e interactiva, pagina nu are functionalitate, nu vrem sa o facem doar asa sa fie, vrem un learning curve acolo"

Translation: don't move to Jobs. Learning is unfinished. The user wants:
1. Nothing external — the course must LIVE inside OpenRadar.
2. Interactive, not a poster.
3. A real "learning curve" — progression, retention, in-app reading.

## What exists today vs what the user wants

| Today | Wanted |
|---|---|
| Skill tree visual (Cytoscape.js) — pretty but read-only | Skill tree = real progression (locked/unlocked, completion %) |
| 15 chapter chips in grid | Chips = navigable lessons with state |
| Detail panel with Methods/Verifiers/Build this + "→ Deschide în AI Road" | Detail panel = full reading experience with embedded content |
| Each chapter is a metadata row (2-3 sentences blurb) | Each chapter = a real lesson (80-120 lines of content alr exists in `ai-beginners-guide/index.html`) |
| No progress tracking | Streak, XP, completed chapters, heat map |
| No interaction within chapter | Quiz / checkpoint per chapter → verifies "did you really get it?" |
| Pillar path visualization only | Pillar path enforcement — pillar N+1 stays locked until N is complete |

## Research findings (synthesized)

### 1. In-app learning UX 2026 — what works
**Duolingo** (300M+ users, $3.7B valuation) runs on:
- Play first, profile second (no setup before value)
- Loss aversion via streaks
- Variable reward XP
- Adaptive difficulty
- Distributed onboarding (tooltips when needed, not upfront)
[Source: [925studios Duolingo breakdown](https://www.925studios.co/blog/duolingo-design-breakdown)]

**Brilliant**: "Learn by doing" — every concept is an atomic interactive problem with immediate feedback. No long walls of text. The lesson IS the interaction. [Source: [brilliant.org](https://brilliant.org/)]

**Headway**: 15-minute micro-lessons. Books broken into swipeable atomic cards (Insight → Action → Challenge). Audio + visual reinforcement. [Source: [Headway](https://apps.apple.com/ph/app/headway-daily-micro-learning/id1457185832)]

**Mimo / Codecademy**: in-app code editor with step-by-step + immediate feedback. No link out.

**Common pattern**: keep the user IN the app. Every interaction reinforces the loop. The "aha" moment happens INSIDE the lesson, not in a tab.

### 2. Skill tree as actual progression
SkillTree (study management app), Duolingo path view, Brilliant course tree all use:
- **Locked vs unlocked nodes** (no grey dots, clear lock/unlock state)
- **Path indicators** (next recommended step is highlighted)
- **Completion rings** (% or checkmark per node)
- **Prereq enforcement** at UI level (can't even click locked nodes meaningfully)
[Source: [SkillTree](https://apps.apple.com/us/app/skilltree-skilltree-lear/id6747299222)]

### 3. Interactive textbook patterns
Modern in-app lessons use **chunked cards** (UX Collective: progressive disclosure reduces cognitive load), **inline quizzes**, **audio + visual reinforcement**, **check-your-understanding gates** between sections. [Source: [UX Collective](https://uxdesign.cc/ux-chunking-a-new-digestible-product-design-process-b5207ce1579f)]

### 4. Retention loops
- **Streaks** — Duolingo's #1 retention mechanism (loss aversion)
- **Daily goal** — "Today: 1 lesson" keeps it bite-sized
- **Spaced repetition** — Anki's SM-2 / SuperMemo FSRS algorithm, returns to weak points at increasing intervals
- **Achievement milestones** — "Chapter 5 complete!" + small XP bump

### 5. Atomic chapter structure
The emerging standard for in-app lessons is the **Hook → Concept → Example → Try → Build → Verify** flow:
- Hook (why this matters in 30 seconds)
- Concept (the actual teaching, 1-2 screens)
- Example (concrete demonstration)
- Try (small interactive prompt or "predict what happens")
- Build (apply to your own context)
- Verify (check yourself against the verifiers)

This is the **microlearning atomic unit**. It's what makes Brilliant, Headway, Mimo feel bite-sized.

## Concrete plan for OpenRadar Learning v1.0

The existing `ai-beginners-guide/index.html` already has 80-120 lines per chapter for all 15. We DON'T re-write content — we IN-LINE it into the Streamlit app as a multi-section lesson reader.

### Phase A · In-app lesson content (the big one)
For each of 15 chapters, render a multi-tab/section lesson reader directly in Streamlit:

| Section | Source | Render as |
|---|---|---|
| **Hook** | new (1 sentence) | quote-style block |
| **Concept** | existing HTML body | rendered markdown (st.markdown) |
| **Example** | existing HTML example code | fenced code block |
| **Try** | interactive prompt (e.g. "now write your own") | text area + submit |
| **Build** | existing `ch.build_this` | gold callout |
| **Verify** | existing `ch.verifiers` | sage checklist (now interactive checkboxes) |

**Tech**: a new `app.py` route + `learning/reader.py` that splits each chapter HTML on heading boundaries + injects the new sections. Layout: tabs or accordion.

**Cost**: ~1 session of careful work. The HTML parser already exists implicitly (BeautifulSoup is in requirements).

### Phase B · Interactive checkpoints
End-of-chapter **Verify** becomes a real check:
- Replace 3-4 plain verifiers with `st.checkbox` rows
- On all-ticked → reveal "Mark complete" button
- One click → chapter moves to "completed" set in `st.session_state`
- Pillar nodes update color from grey → gold on skill tree
- Next pillar unlocks

**Visual**: big satisfied checkmark ✓ — that's the dopamine.

### Phase C · Retention & progression
- **Streak counter** in Learning section header: "🔥 5 days · 8 of 15 chapters"
- **Today's lesson** on Azi section: pulls the next incomplete chapter into a "Start here" card
- **Heat map** (small): last 30 days activity, mono styled, color = pillar completed
- **Progress bar**: "8/15 chapters · 53%" with 7 pillars highlighted in gold

**Tech**: `session_state` with `completed_chapters: Set[str]`, `streak_data: dict[date, int]`, computed on every render.

### Phase D · Gated progression (lock state)
- Pillars (ch1,3,5,8,11,14,15) start locked except ch1
- Each pillar unlocks when its predecessor is completed
- Non-pillar chapters unlock when their prereqs are met
- Locked chips: greyed out + 🔒 icon + tooltip "Complete Ch 1 first"
- Skill tree shows locked nodes with dashed grey stroke instead of gold

### Phase E · (optional, post-v1.0) Spaced review
- For each chapter's key concepts (one per chapter), generate a flashcard
- `st.session_state["due_reviews"]` queues cards based on completion date
- Quick "Review 3 cards" prompt at top of Learning section
- Simple SM-2-lite: again/hard/good/easy

**Skip for now** — this is its own session of work and the user didn't ask for it.

## Recommended sequencing

| Session | What ships | Effort |
|---|---|---|
| **1. Phase A** | In-app lesson reader for all 15 chapters | ~2h (parsing + styling) |
| **2. Phase B + D** | Interactive verify + lock state + pillar unlock | ~2h |
| **3. Phase C** | Streak, heat map, today's lesson on Azi | ~1h |
| **4. Polish** | Domain colors per section, animations, dark/light media queries, ship | ~1h |

**Phase A** is the single biggest unlock because it changes "Learning tab has a link" → "Learning tab IS the course."

## Key risks & decisions

1. **HTML parsing fragility** — the existing `ai-beginners-guide/index.html` has all 15 chapters in one file. A small parser script extracts each chapter on first load, writes to `learning/content/<ch>.json` (cached). Falls back to current meta-only data if parse fails.

2. **Long page vs tabs** — 15 chapters × ~100 lines of content = a lot of scrolling. Use `st.tabs` inside the detail panel: [Read][Methods][Practice][Build]. Or a sub-navigation at the top of the chapter.

3. **Sidebar sticky nav** — add a "Chapter outline" inside the detail panel showing all sections of the current chapter with anchors (#hook #concept #example #try #build #verify).

4. **The lock state risk** — if we lock ch2 until ch1 is done, what's the first-time-user UX? Answer: ch1 is always unlocked by default. Streak/progress shown as "0% — start with The Magic Kitchen" + a big "Start" button. Empty state = motivating, not punishing.

5. **No external links** — explicit user constraint. Strip the "→ Deschide capitolul X în AI Road" link entirely from v1.0. The user reads, practices, and verifies all inside OpenRadar.

## Closing

The current Learning tab is a trailer. The user wants the movie. **Phase A is the biggest single change** — it transforms the chapter detail panel from "chapter metadata" into the actual lesson content (in-app). Once Phase A lands, Phases B-D each add meaningful interaction on top of real content. The order matters: content first (Phase A), then engagement (Phase B-D).

---

## Sources

1. [Duolingo UX Breakdown: Why 50M+ Users Show Up Every Day (2026)](https://www.925studios.co/blog/duolingo-design-breakdown) — full deep-read
2. [Brilliant | Learn by doing](https://brilliant.org/) — atomic interactive problems
3. [Headway - Daily Micro Learning](https://apps.apple.com/ph/app/headway-daily-micro-learning/id1457185832) — 15-min micro-lessons
4. [Mimo: Learn Coding](https://mimo.org/) — in-app code editor
5. [SkillTree App — RPG-style study management](https://apps.apple.com/us/app/skilltree-skilltree-lear/id6747299222)
6. [UX Chunking: progressive disclosure methodology](https://uxdesign.cc/ux-chunking-a-new-digestible-product-design-process-b5207ce1579f)
7. [Best Spaced Repetition Apps 2026: Anki, Chunks, Duolingo & More](https://chunks.app/blog/best-spaced-repetition-apps-2026)
8. [Best Microlearning Apps 2026](https://chunks.app/blog/best-microlearning-apps-2026)
9. [Duolingo gamification explained — retention 12% to 55%](https://strivecloud.io/blog/gamification-examples-boost-user-retention-duolingo)
10. [UX and Gamification in Duolingo](https://uxplanet.org/ux-and-gamification-in-duolingo-40d55ee09359)
11. [Apple Education Community — Chunking Texts with Scaffolding](https://education.apple.com/resource/250012502)
12. [LEAP — Live Experiments for Active Pedagogy (arXiv 2601.22534)](https://arxiv.org/abs/2601.22534)
13. [The example of a four-tier test (ResearchGate)](https://www.researchgate.net/figure/The-example-of-a-four-tier-test_fig3_356644820)
14. [Edpuzzle — interactive video lessons](https://www.edpuzzle.com/)
15. [User Guiding: Duolingo Onboarding UX Breakdown](https://userguiding.com/blog/duolingo-onboarding-ux)
16. [Growth.Design: Duolingo's User Retention Case Study](https://growth.design/case-studies/duolingo-user-retention)
17. [Headway App Review: 7-Day Honest Verdict](https://www.shortform.com/blog/hub/product/headway-app-review/)
18. [7 Features of the Headway App](https://www.makeuseof.com/features-headway-app-help-grow-self-learning/)

## Methodology

5 web searches (multi-source, 12-16 results each) + 1 deep-read fetch (Duolingo breakdown). 18 unique sources synthesized. Cross-checked atomic structure, retention loops, and skill-tree gating patterns against 3+ independent sources each.
