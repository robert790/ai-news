# OpenRadar Theme v0.1

> **Status:** Locked contract (PR #36). Future visual PRs must follow this.
> **Audience:** Anyone touching `theme.py`, `app.py`, or any section's visual structure.
> **Replaces:** ad-hoc per-section styling. Prior art (PR #32 Home chassis, PR #33 topnav breakpoint, PR #34 terminal section shell, PR #35 Prompt Kits performance) is absorbed here as the accepted baseline.

This document is the source of truth for OpenRadar's visual language. It is
**docs-only** at the time of writing — no `app.py` or `theme.py` changes ship
with PR #36. It exists so future visual PRs are reviewed against an explicit
contract instead of vibes.

---

## A. Theme identity

OpenRadar's visual language is **retro-futuristic radar terminal / industrial
AI workbench**.

Inspirations:
- Old radar consoles
- CRT terminals
- Field instruments and bunker dashboards
- Phosphor UI (P1 phosphor green, amber, dim olive)
- Worn graphite metal with subtle panel seams

Explicitly **not**:
- A direct Fallout clone (no Pip-Boy chrome, no vault-tec typography)
- Generic cyberpunk (no neon-rain, no rain-soaked Tokyo, no chrome spikes)
- Neon gamer UI (no hot pink, no RGB, no glitch effects)
- Apple-ish glassmorphism (no backdrop-blur everywhere, no frosted layers)

The feel should read like a **field instrument that has been in service for a
while** — calm, deliberate, slightly worn — not a synthwave poster.

**Utility before aesthetics.** A visual decision that makes the app
easier to use beats one that just looks nicer. Decoration exists to
reinforce function, never to replace it.

---

## B. Current accepted baseline (post-PR #35)

| Surface | Accepted form |
|---|---|
| **Home** | Full radar-console experience. PR #32 (radar-terminal Home) is the locked chassis. |
| **non-Home sections** (Tools / Prompt Kits / Jobs / Learn) | Terminal module / framed workbench pages. PR #34 added `.ort-module-head` and `.ort-module-card` primitives for this. |
| **Topnav** | Compact radar bar. PR #33 set the mobile collapse breakpoint at 640px. |
| **Prompt Kits list** | Capped at 24 items on cold load + "Show 24 more" pagination (PR #35). |
| **HF runtime** | Green after PR #35; all six routes 200. |

**Rule of thumb:** Home is the only place where the full radar-console chassis
is allowed. Other pages should *feel* like terminal modules, not like Home
clones with different content.

---

## C. Design tokens / language

### Color roles

| Role | Use |
|---|---|
| `near-black` (~#0B0F0D) | Page background. |
| `graphite metal` | Panel surfaces, recessed modules, card fills. |
| `phosphor mint/green` | Primary accent, active state, brand color. |
| `muted olive` | Secondary accent, dim labels. |
| `amber warning` | Tertiary accent, selected state, warnings. |
| `dim gray` | Body text, descriptions, muted UI. |
| `bright text` | Headlines, titles, primary content. |

**Rule:** Phosphor mint/green is the only "loud" color. Amber is used sparingly
for selection and warning. Everything else is near-black/gray with restrained
phosphor tints.

### Materials

- Recessed metal panels (subtle inset shadows + 1px hairline borders)
- Phosphor glass effect for the active state (low-opacity mint glow, not a
  full-bloom neon glow)
- CRT edge softening (rounded corners, 4-5px radius — not pills, not sharp)
- Worn panel seams (1px hairline borders, sometimes dashed for "less important"
  separators)
- Subtle scan texture (low-opacity, must respect `prefers-reduced-motion` and
  must not reduce readability)
- Thin borders (1px solid, never 2px or heavier)

### Typography

- **Readability first.** Body text is the highest priority.
- Mono labels for eyebrows, button text, captions, metadata
- Strong but restrained headings (not oversized, not all-caps scream)
- No cramped gimmicks (no letter-spacing pushed to 0.4em on body text)
- No more than 2 type families per page (mono + 1 readable text family)

### Motion

- Subtle radar sweep (low-opacity, slow, easily dismissed by users who want
  stillness)
- Phosphor glow transitions (~150-200ms ease)
- Respect `prefers-reduced-motion` — radar sweep and phosphor glow must
  disable or hard-pause
- No spinning logos, no marquee text, no animated background loops

### Spacing

- Calm dashboard density — not Twitter-feed dense, not Apple-launchpad sparse
- 8px spacing scale (8 / 16 / 24 / 32 / 48)
- Vertical rhythm: headings, body, and CTAs should align to the same grid
- Cards and modules: consistent 1rem–1.5rem internal padding
- **No** noisy feed layouts (multi-column ticker rows, ping-pong cards, etc.)

---

## D. Component rules

### Home chassis

- Locked per PR #32. **Do not redesign casually.**
- Small targeted edits inside the existing Home section are fine.
- Structural redesign requires explicit owner approval and a separate PR.

### Section header / module shell

- Use `.ort-module-head` for non-Home section headers (PR #34 primitive).
- Tightens the section header so eyebrow + h1 + caption sit inside a clear
  recessed module panel with a phosphor left-edge accent.
- Do not stack two `section_head()` calls on the same page; demote the second
  to an `.or-eyebrow` block instead.

### Action cards

- Use `.ort-module-card` (PR #34 primitive) on every non-Home path-kit card.
- Each card has separated label / title / body + an `st.button` CTA inside a
  bordered container.
- Cards are uniform 4-up rows on desktop, 2-up on tablet (~880px), 1-up on
  mobile (~640px).
- The CTA button must hydrate on cold load — see "Prompt Kits heavy list rule"
  below.

### Buttons / CTAs

- Restrained pill or rectangular shape (not both at once)
- Phosphor mint for primary, amber for selected, transparent for secondary
- Mono font, 0.66–0.7rem, letter-spacing 0.14–0.18em, uppercase
- Hover: subtle background shift, no dramatic gradient or scale transform
- Active state: same shape, brighter phosphor tint, 1px border

### Nav (topnav)

- Compact radar bar (PR #33)
- 2-row collapse at ≤640px
- Active tab: phosphor left-edge accent + slightly brighter text, no big pill
- Hover: subtle underline / dot, never a colored background

### Lists / results

- Calm density — at most 2 visual levels (header + body, no header +
  subheader + meta + tags + footer)
- Mono labels above the result list, normal text for the result rows
- No card-grid for the Prompt Bible — use a clean vertical stack
- **Always paginate or virtualize any list that could exceed ~50 items**

### Prompt Kits heavy list rule

> The Prompt Bible ships 1,137 prompts. Rendering the full list on cold load
> emits ~9,365 `stElementContainer` elements, which delayed Open button
> hydration to ~18–22 seconds. **Never render thousands of widgets on cold
> load again.**

This rule applies anywhere in the app where a list could grow large:

- Prompt Bible: cap initial render at 24, "Show 24 more" pagination (PR #35)
- Any future list (job feed, repo list, etc.) must follow the same pattern:
  cap initial render + pagination, OR lazy-load on scroll/click
- Cold-load widget budget per route: stay under **~500 element containers**
  unless explicitly justified

---

## E. Do / Don't

### Do

- Preserve readability. If a visual decision hurts reading, it's the wrong
  decision.
- Use restrained terminal detailing. One phosphor accent per element max.
- Keep mobile first-class. Design mobile first, then scale up. 393/414/768/1440
  viewports are the QA bar.
- Prefer scoped, reusable classes (`.ort-module-head`, `.ort-module-card`,
  etc.) over per-section one-off CSS.
- Keep performance gates. Every visual PR must preserve the
  ~620ms hydration of the Prompt Kits action cards (PR #35 baseline).

### Don't

- **Don't** clone the full Home chassis onto every other page. Other pages
  should feel like terminal modules, not Home clones.
- **Don't** add broad invisible CSS hacks (`* { display: none }`,
  `opacity: 0 !important` on a class to hide a bug, etc.).
- **Don't** add noisy global scanlines, glitch effects, or animations that
  reduce readability or trigger `prefers-reduced-motion` complaints.
- **Don't** create pink / neon / gamer styling. The brand is phosphor
  mint/green + amber + dim gray, not rainbow.
- **Don't** hide broken widgets with CSS. If a button is stuck in skeleton
  state, fix the cause (e.g. PR #35), don't `display: none` the skeleton.
- **Don't** regress Prompt Kits hydration. The 24-item cap and pagination
  are part of the contract; removing them without a replacement strategy
  re-introduces the 20-second cold-load bug.

---

## F. Future implementation backlog

Ranked small PRs, lowest-risk first:

1. **Apply terminal module shell to Learn page** — Learn still uses legacy
   styling; bring it up to the `.ort-module-head` / `.ort-module-card` baseline.
2. **Improve Home chassis material depth / reflections** — small targeted
   polish on the locked Home chassis (PR #32). Subtle inset shadows, slightly
   more visible panel seams. Do not redesign.
3. **Polish action-card buttons inside module cards** — ensure the Open
   button sits flush with the card border, with the same pill style as the
   filter pills. Scoped to `.ort-module-card .stButton`.
4. **Add reusable terminal token comments/classes in `theme.py`** — document
   the existing CSS variables (color roles, spacing scale, type ramp) as
   named tokens at the top of `theme.py` for future contributors.
5. **English copy cleanup: "prompturi" → "prompts"** — sweep the remaining
   Romanian strings on the Prompts tab. The count line and result count were
   already updated; the section header, the empty-state message, and the
   expander label still say Romanian.
6. **Mobile radar/home polish** — small improvements to the mobile experience
   on Home and the topnav. Don't redesign; tighten spacing and tap targets.
7. **Later (not PR-sized): evaluate Next.js / Tailwind only if Streamlit
   blocks the desired interaction level.** This is a strategic decision, not
   a small PR. Triggered by a concrete UX blocker, not by a wishlist.

---

## G. Acceptance checklist for future visual PRs

Before opening a visual PR, confirm:

- [ ] **Home unchanged** unless the PR's scope explicitly includes Home.
- [ ] **All routes return 200** (Home / Tools / Prompt Kits / Jobs / Learn).
- [ ] **Visual checks at 393 / 414 / 768 / 1440** — no horizontal overflow,
      no clipped text, no broken layouts.
- [ ] **Prompt Kits remains fast** — action buttons hydrate within ~1 second
      of cold load. No widget-count regression in the results loop.
- [ ] **No workflow / HF changes** — no `.github/`, no `Dockerfile`, no
      `scripts/deploy*` edits.
- [ ] **No topnav / global theme changes** unless the PR's scope explicitly
      includes them.
- [ ] **Screenshots / contact sheet** for any visual change. Save under
      `/tmp/browser-qa/openradar-pr<N>-<short-name>/` and build
      `/tmp/openradar-pr<N>-<short-name>-contact-sheet.png`.
- [ ] **Tests pass**: `git diff --check`, `py_compile`, `pytest`.
- [ ] **Commit message + PR title** follow the existing convention
      (`feat(scope): …`, `fix(scope): …`, `perf(scope): …`, `docs(scope): …`).

---

## H. Related docs

- `HANDOFF.md` — operational state, profile, rollback, do-not-continue.
- `docs/WORKFLOW.md` — PR preview / deploy workflow.
- `docs/decisions.md` — historical product / tooling decisions.
- `AGENTS.md` (repo root) — Hermes agent coding rules (do not duplicate here).

This document is **adjacent to** HANDOFF.md, not a replacement. HANDOFF.md is
the live operational state; THEME.md is the stable visual contract.
