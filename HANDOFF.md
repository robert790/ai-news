# Handoff · OpenRadar (Ziarul Digital)

> Romanian-first AI news + a 10-chapter learning path.  
> Last updated: 2026-06-30 · Streamlit 1.50 local / 1.32 on HF Spaces.

---

## 1. What this is

OpenRadar (was "Ziarul Digital") is a Streamlit app with **5 sections**:

| Section    | Tab | What it does                                                                 |
|------------|-----|------------------------------------------------------------------------------|
| **Groq**   | ☀   | Daily AI briefing — 3 stories, 1 takeaway, ask-the-curator chat.             |
| **News**   | ◌   | Hacker News AI stories, summarized in Romanian (DeepSeek fallback).           |
| **Learning** | ❡ | 10-chapter category walkthrough (history → LLMs → diffusion → agents → career). |
| **Jobs**   | ◆   | Skill-gap matcher between your CV and AI infra roles (Romania focus).         |
| **Prompts** | ✦ | Curated prompt library with copy buttons.                                    |

Hero identity is **OpenRadar**. First tab is named **Groq** (a curator persona in
the Learning chapters — NOT a Romanian word "azi"; that means "today" and is
preserved in chapter body text).

---

## 2. Where the code lives

```
/Users/zero/Minimax Projects/ai-news/
├── app.py                    1058 lines · top nav + section dispatch + 5 renderers
├── theme.py                  1007 lines · ~28KB CSS (warm dark, amber/sage/coral)
├── config.py                  36 lines  · env-driven config (DEEPSEEK etc.)
├── prompts.py                ~5.5KB    · prompt library data
├── tips.py                   ~4.7KB    · tip system
├── learning/
│   ├── chapters.py           1301 lines · 10 Chapter dataclasses, methods, verifiers
│   ├── learning_render.py     659 lines · detail panel, methods, verifiers, next-card
│   ├── insight.py             230 lines · Groq's take + Ask Groq (LLM chat)
│   ├── timeline.py            157 lines · 7-era SVG timeline (era 1-7 → ACUM)
│   ├── cross_refs.py          ~100     · chapter pointer relationships
│   ├── skill_tree.py          ~?        · prereq graph (Cytoscape planned)
│   ├── reader.py              ~?        · content loader
│   ├── parser.py              ~?        · markdown → HTML
│   ├── chapter_tags.py        ~?        · domain tag helpers
│   └── content/                         · chapter raw markdown + assets
├── llm/                       · DeepSeek client (OpenAI-compatible)
├── scrapers/                  · HN + findarepo fetcher
├── prompts_data/              · prompt library JSON
├── data/                      · cached fetch results
├── rag/                       · RAG over chapter content (placeholder)
├── tests/                     · smoke tests
├── docs/
│   ├── LEARNING_TAB_PLAN.md   · original plan
│   └── decisions.md           · design decisions log
├── .env.example
├── requirements.txt           · streamlit, httpx, bs4, openai, dateutil
├── DEPLOY.md                  · HF Spaces deploy notes
├── STRUCTURE.md               · original file map
├── README.md                  · public-facing (HF metadata frontmatter)
└── HANDOFF.md                 · this file
```

Total app code: ~4,400 lines across 6 main files (app.py + theme.py + 4 learning
modules). The visual layer lives entirely in `theme.py` — one CSS dump fed via
`st.markdown(..., unsafe_allow_html=True)` at app start.

---

## 3. Tech stack

- **Python 3.9** (HF Spaces) / 3.13 (local)
- **Streamlit 1.50** local · **1.32** on HF (pinned via Dockerfile in HF Space)
- **httpx** for HTTP, **beautifulsoup4** for parsing
- **openai** client pointed at DeepSeek (`https://api.deepseek.com`, OpenAI-compatible)
- No frontend build step. No JS framework. CSS only.
- **No** pydantic, **no** SQLAlchemy, **no** LangChain — kept minimal for HF cold start.

---

## 4. Running locally

### Prerequisites
- macOS (Apple Silicon · M-series)
- Python 3.9+ (3.13 works fine; 3.9 needed for HF parity)
- venv at `./.venv`

### One-time setup
```bash
cd "/Users/zero/Minimax Projects/ai-news"
python3 -m venv .venv
arch -arm64 ./.venv/bin/python3 -m pip install -r requirements.txt
cp .env.example .env  # edit DEEPSEEK_API_KEY if you want live summaries
```

> **Why `arch -arm64`?** The venv was created with a pydantic-core wheel
> that only ships x86_64. Running the default `python3` (arm64) fails with
> `pydantic_core` arch mismatch. Always use `arch -arm64 ./.venv/bin/python3`.

### Dev server
```bash
nohup arch -arm64 ./.venv/bin/python3 -m streamlit run app.py \
  --server.port 8521 --server.headless true --browser.gatherUsageStats false \
  > /tmp/streamlit_8521.log 2>&1 &
disown
sleep 5
open http://localhost:8521
```

Port **8521** is the redesign workspace. Port **8501** is the original
Ziarul Digital background dev server. Don't mix them.

### Restart after theme.py or app.py changes
```bash
ps aux | grep -E 'streamlit.*8521' | grep -v grep | awk '{print $2}' | xargs -r kill
sleep 3
# then start fresh as above
```

> **Streamlit 1.32 caches CSS** — hard restart needed after big `theme.py`
> edits, not just browser refresh.

---

## 5. Deployment · Hugging Face Spaces

- Repo: `https://huggingface.co/spaces/vrobert94/ai-news`
- Live URL: `https://vrobert94-ai-news.hf.space/`
- SDK: Streamlit, pinned to **1.32.0** (Dockerfile in HF Space)
- Deploy: `git push huggingface main` (auto-rebuilds ~60s)
- Deep-link: `?section=learning&ch=ch1` works in both `app.py` and `st.query_params`

> **HF Spaces 1.32 quirks** — don't use these Streamlit 1.50+ features:
> - `st.columns(..., vertical_alignment="center")` → use `_columns()` helper
> - `st.query_params` is OK on both
> - Verify any new feature with both versions before shipping

---

## 6. Code conventions (enforced)

These are the rules I (Mavis) have learned from working with Robert. Every
new file/edit should pass them.

1. **No em-dashes (U+2014) anywhere.** Use `:` for appositive, `·` for section
   separator, `.` for hard break, `,` for proper-name joiner. Polish copy only.
2. **No "Mavis" / "Mavis Agent" / "minimax Code Agent" in user copy.** Use
   "minimax Code Agent + CLI" in tech blocks, or omit entirely.
3. **No repetition across sections.** Don't restate the hero intro in the right
   sidebar. Don't restate the method in the verifier.
4. **Romanian-first copy** — chapter body, UI labels, button text. English only
   for technical terms in code blocks.
5. **CSS lives in `theme.py`** — no inline `<style>` in `app.py` except for
   data-driven styles (e.g. accent colour per chapter domain).
6. **Inline styles allowed** in `learning_render.py` for one-off blocks (Methods
   callout, Următorul capitol card) when the block is small and self-contained.
7. **`st.button` over `st.radio`** for nav and toggles — radio circles fight CSS.
8. **Never use `rm`/`rm -rf`** — use `mavis-trash <path>` for deletions.
9. **Never edit source files via `sed -i`/`> file`** — bash auto-blocker. Use
   Edit tool with prior Read.
10. **CV/Learning copy must NOT pretend to be senior engineer.** Robert's angle:
    AI-powered business operator (production, Romania, multi-tool stack).
11. **Project lives in `/Users/zero/Minimax Projects/`, not
    `/Users/zero/.minimax-agent/projects/`.** User has a visible folder for
    projects; the hidden one is daemon internal.

---

## 7. What we built in this session (chronological)

### Top nav redesign (commit `eb79c14`)
- Killed Streamlit sidebar. Replaced with `st.columns([1.4, 4.2, 1.6])` row:
  brand · pills · status. 5 pill buttons with `type="primary/secondary"`
  toggled by `st.session_state.active_section`.
- `?section=foo` deep-link via `st.query_params`.
- Mobile (≤720px) breakpoint via CSS `:has()` selectors — stacks into 3 rows.
- Backwards-compat helper `_columns()` drops `vertical_alignment=` on 1.32.

### Learning redesign (commits `c97d585` → `a01ad4f` → `8e4ec18` → `0406e41`)
- Killed "Project Erica" entirely (was a fictional persona arc).
- Replaced with **10-category walkthrough**:
  CH1 Fundamente · CH2 LLMs · CH3 Prompting · CH4 Vision AI · CH5 Diffusion ·
  CH6 Speech & Audio · CH7 Embeddings & RAG · CH8 Agents · CH9 Cum construiești
  · CH10 Aplică.
- New `DOMAINS` dict: `history, llm, prompting, vision, diffusion, speech, rag,
  agents, tools, career` (replaces `story, concepts, skills, policy, fusion`).
- Timeline rewritten: "ERIKA" → "ACUM", subtitle "7 ERE · 10 CATEGORII · UN
  DE ACUM".
- Detail panel: number + domain + era + body + verifiers + build-this.

### Azi → Groq rename (commit `345da6d`)
- Section key `azi` → `groq`, render_azi → render_groq, ask_azi → ask_groq.
- "Ask Azi" expander → "Ask Groq". `insight.py` SYSTEM prompts now address
  Groq. Romanian word "azi" (= today) **preserved** in chapter body.

### Methods overlay (commit `44cab4a`)
- `@dataclass Method(name, summary, when_to_use, recommended)` populated on
  every chapter — 1 MAIN + 1 alternative per chapter.
- Visual: ◆ MAIN = amber-gradient bordered callout; ○ alts = collapsed expander.
- Method names are memorable: "Cronologia pe frigider", "Detective de
  token-uri", "Whisper pe viața ta", "5 linii, 1 Ollama", "Aplică azi".

### Next-chapter card + methods progress (commit `2af3a5d`)
- Sage-bordered **"Următorul capitol"** card above prev/next buttons. Shows
  next chapter number + title + subtitle + next MAIN method name.
- **"Am făcut metoda X azi"** checkbox under each method (main + alts).
- Right sidebar now shows **"◆ N metode bifate"** below the chapter progress
  bar. Counts across all 10 chapters.

---

## 8. State architecture

### session_state keys used
- `active_section` — `"groq" | "news" | "learning" | "jobs" | "prompts"`
- `selected_chapter` — `"ch1" .. "ch10"`
- `completed_chapters` — `set[str]`
- `verifier_{ch.id}_{i}` — bool (per chapter verifier checkbox)
- `method_done_{ch.id}_main` — bool (MAIN method done)
- `method_done_{ch.id}_alt_{i}` — bool (alt method done)

### Cross-chapter computation
- Right sidebar counts methods across all chapters via list comprehension over
  `ch_list` (not just current chapter).
- No persistence — refresh = lose progress. Acceptable for v1; see §11.

### Render order in app.py
1. `render_top_nav()` — sets `active_section`
2. If `?section=` in URL, sync to `active_section`
3. Dispatch table:
   ```python
   if active == "groq":    render_groq()
   elif active == "news":  render_news()
   elif active == "learning": render_learning()  # left/right cols
   elif active == "jobs":  render_jobs()
   elif active == "prompts": render_prompts()
   ```

---

## 9. File edit recipes (the traps we hit)

These are the things that bit us. Future contributors should NOT rediscover them.

### Streamlit CSS injection
- **`st.markdown('<div>')` does NOT wrap subsequent elements.** Rendered as a
  sibling of `st.columns` children. Decorative wrapper divs are empty in DOM.
- **`key=` becomes `class="st-key-key_name"`, not `data-key`.** Use selector
  `[class*="st-key-nav_"]` to target Streamlit widgets.
- **BaseWeb radio markup**: `<label data-baseweb="radio"><div><div></div></div>
  <input type="radio">...</label>`. Hide via `> div:first-child { display: none }`.

### Streamlit 1.32 vs 1.50
- Don't use `vertical_alignment=` kwarg on `st.columns` (1.50+ only).
- `_columns()` wrapper in `app.py` drops the kwarg conditionally.
- `st.query_params` works on both.

### theme.py key dict
- `FONTS` dict has only 3 keys: `display, ui, mono`. **No `serif`.** Use
  `f['display']` (Newsreader) when you want serif.

### Bash traps
- `sed -i` on source files = blocked by bash auto-classifier.
- `> file` overwriting source = blocked.
- Use Edit tool (anchored oldString/newString) for source edits.
- For huge transforms (500+ lines), use Python to write to `/tmp/`, then
  Edit tool to copy blocks in. Don't `cp /tmp/x dest.py` either — blocked.

### Romaniantypographic quotes
- `„` (U+201E) inside Python `"..."` strings breaks the literal. Use `« »` or
  escape: `\"`. Hit on chapter rewrite at line 847.

### Wide CSS injection inside `st.markdown`
- Style blocks inside f-strings need `{{` and `}}` to escape Python braces.
- Pattern: `<style>.foo {{ color: red; }}</style>` (double braces).

### Chapter dataclass regex injection
- Adding methods to all 10 chapters: regex like `\n    \)\n` fails because
  the closing paren was at indent 1 (not 4). Better: walk parens from
  `CH<N> = Chapter(` opening to find the matching `)`.

---

## 10. Visual identity

### Colour palette (theme.py: COLORS)
- `--bg` — deep warm dark (almost-black with brown undertone)
- `--bg-sidebar` — slightly lighter brown
- `--surface` / `--surface-2` — card backgrounds
- `--accent` — per-chapter domain colour:
  - history: sage green
  - llm: amber
  - vision: sky blue
  - diffusion: coral
  - speech: lavender
  - rag: amber secondary
  - agents: gold
  - tools: sage secondary
  - career: amber primary
- `--text` — cream (#f4ede0)
- `--text-muted` — `#c4b9a7` / `#cdc4b1` / `#9a8f7c`
- `--text-dim` — `#6a6058`

### Typography
- **Display**: Newsreader (serif, italic, weights 300-700) — for chapter titles, body
- **UI**: Inter (sans, weights 300-700) — for nav, labels, buttons
- **Mono**: JetBrains Mono — for tags, eyebrows, verifiers, counters
- All loaded from Google Fonts CDN via single `@import` in theme.py.

### Visual signatures
- **Eyebrow** = uppercase mono 0.6rem with 0.16em letter-spacing + accent colour.
- **Card** = border-left 2-3px solid accent + 6-10px border-radius + light
  background gradient.
- **Methods MAIN** = amber gradient with `◆` glyph prefix.
- **Methods alts** = collapsed expander with `○` glyph prefix.
- **Verifiers** = sage `▸ Ai înțeles?` eyebrow + green checkboxes.
- **Build this** = gold `⚡ Fă asta ACUM` callout.
- **Următorul capitol** = sage-green bordered card with gradient.

---

## 11. Where this is going (next moves)

### Short-term (1-2 sessions)
- [ ] **Persist progress** — write `completed_chapters` + methods to disk
      (`./data/progress.json` or similar) so refresh doesn't reset.
- [ ] **Skill tree visual** — Cytoscape.js graph showing 10 chapters as nodes
      with prereq edges + domain colour + complexity 1-4 as node size. Already
      partly scaffolded in `learning/skill_tree.py`.
- [ ] **Pillar gold badges** — gold dashed line between consecutive pillars
      in the skill tree (Sebastian Rey blueprint signature).
- [ ] **Mobile polish** — full check at ≤720px including Methods block,
      Următorul capitol card, and right sidebar.

### Medium-term (1-2 weeks)
- [ ] **Real Groq LLM call** — `insight.py` currently has DeepSeek fallback.
      Swap model based on user-set env var (GROQ_API_KEY vs DEEPSEEK_API_KEY).
- [ ] **RAG over chapter content** — `rag/` placeholder exists. Embed chapter
      bodies + cross-refs → answer "where does ch4 mention Vision?" queries.
- [ ] **Jobs section wired up** — currently has UI scaffold, no skill-gap
      matcher logic.
- [ ] **Onboarding modal** — first-visit 30-second tour: "click here → learn → check → next".

### Long-term (vision)
- OpenRadar becomes **the Romanian AI hub** — news + learning + jobs + prompts,
  with a curator persona (Groq) that ties them together.
- Three tiers of users:
  1. **Casual** — just scan the news + tips.
  2. **Learning** — walk the 10 chapters, tick verifiers, do rituals.
  3. **Hunting** — finish ch10 "Aplică", then jump to Jobs, get matched.
- White-label friendly: themes are 1 CSS file, content is 1 Python module,
  persona is 1 dataclass.

---

## 12. Gotchas for the next environment

If you're continuing this project on a different machine (not Robert's Mac):

1. **The Streamlit version matters.** If you're on Linux without HF pinning,
   use 1.50+. The codebase supports both via `_columns()` helper.

2. **Don't `git push huggingface` from anywhere except Robert's machine** —
   the HF token is in `git remote -v`. On a fresh clone, you'll need to add
   your own HF Spaces remote:
   ```bash
   git remote add huggingface https://huggingface.co/spaces/<your-user>/ai-news
   ```

3. **No DeepSeek key = degraded News tab.** Demo mode returns canned
   summaries. Add `DEEPSEEK_API_KEY=...` to `.env` for real summarization.

4. **No Ollama on this machine.** The Methods overlay mentions "5 linii, 1
   Ollama" as a ch9 ritual — the user runs Ollama locally; the app doesn't.

5. **`venv` is not portable.** The `.venv` is committed in this repo (it's
   already there for some reason) but won't work on Linux — just recreate it:
   `python3 -m venv .venv && pip install -r requirements.txt`.

6. **The `learning/content/` directory has chapter assets.** If you see
   broken images in chapters, that's where to look.

7. **Memories are user-scoped.** Robert-specific copy rules (CV voice, Hermes
   CLI framing) live in `~/.mavis/agents/mavis/memory/robert-context.md` —
   load that file if you're Mavis and writing Robert-facing copy.

8. **Don't add new Streamlit features without checking 1.32 compat.** Test
   locally first, then check HF rebuild. HF rebuilds are slow (~60s) and
   failures are silent in the UI.

9. **No tests written.** The `tests/` folder is a placeholder. The codebase
   relies on visual verification + Python import-time checks.

10. **No CI/CD.** Just `git push`. If you want CI, add a `.github/workflows/`
    later — but not now.

---

## 13. Quick reference · most-touched files

When extending, edit in this order:

1. **`learning/chapters.py`** — add/edit chapter content + methods + verifiers.
2. **`learning/learning_render.py`** — adjust how a chapter renders.
3. **`theme.py`** — add CSS classes for new visuals.
4. **`app.py`** — add new sections or nav tabs.
5. **`insight.py`** — swap LLM prompts.
6. **`.env.example`** — surface new config knobs.

Last thing first: any new visual primitive belongs in `theme.py` BEFORE
`learning_render.py` calls it. Inline styles in `learning_render.py` are OK
for self-contained one-offs (current pattern: Methods + Următorul capitol).

---

## 14. Final state · commit log (latest 10)

```
2af3a5d feat(learning): next-chapter card + methods progress
44cab4a feat(learning): Sebastian Rey BLUE methods overlay (◆ MAIN + ○ alts)
345da6d rename: Azi → Groq (nav tab + learning persona)
0406e41 fix(learning): drop remaining 'Project Erica' copy in app.py + add deep-link
a01ad4f refactor(learning): kill Project Erica, walk through AI categories
4af886b fix(nav): backwards-compatible columns for Streamlit 1.32 (HF)
eb79c14 feat(nav): replace sidebar with top nav (brand | pills | status)
8e4ec18 feat(learning): Redesign chapter detail panel as Drumul Erica arc
c97d585 feat(learning): new chapters + timeline hero + isolated detail panel (in-progress)
8bb92a9 merge feat/learning-groq: TL;DR + Azi's take + cross-refs + Ask Azi
```

All pushed to `origin` (GitHub: `robert790/ai-news`) and `huggingface`
(HF Space: `vrobert94/ai-news`).

---

*If you read this and find a section unclear, the answer is in §6 (rules),
§9 (traps), or §11 (where it's going). If those don't cover it, ask Robert —
he knows what he wants even when he doesn't say it yet.*