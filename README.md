---
title: OpenRadar · AI Career & Tools Radar
emoji: 📡
colorFrom: green
colorTo: yellow
sdk: streamlit
sdk_version: 1.58.0
app_file: app.py
pinned: false
license: mit
short_description: AI career & tools radar · learn, build, apply
---

# 📡 OpenRadar

**AI career & tools radar.** Learn AI · pick the right tools · find the work.

Five tabs: one signal per day, curated tools grouped by use case, a 10-chapter
learning path, role + skill map with real search paths, and prompt kits grouped
by outcome (with the full Prompt Bible below as a power-user layer).

- **Today** ☀ — daily brief, bento of top 3 from each tab, lesson of the day, prompt kit to try.
- **Tools** ◌ — curated by use case: Build / Ship / Write & Decide / Discover. Not a directory.
- **Learn** ❡ — 10 short chapters with a "build this" exercise per chapter. Paths, not a course.
- **Jobs** ◆ — static role + skill map. Search paths to LinkedIn / BestJobs / eJobs / Indeed RO.
- **Prompt Kits** ✦ — outcome-grouped bundles. The full Prompt Bible (1,137 prompts) is below.

## How it works

The app fetches AI-related stories from Hacker News, Hugging Face papers,
GitHub trending and findarepo, summarizes via Groq (OpenAI-compatible, free
tier), with a deterministic fallback when no key is set. The interface is a
warm-dark workspace with sage/amber/coral accents. Learning is offline content
— 10 chapters with methods, verifiers, and a curator persona (Groq). Prompt
Kits are curated bundles pulled from the Prompt Bible data (committed to the
repo — no runtime network dependency).

## Deep links

- `/` — Today (default landing)
- `/?section=news` — Tools, `/?section=jobs`, `/?section=prompts`, `/?section=learning`
- `/?section=learning&ch=ch1` — opens chapter 1 directly
- `/?section=prompts&kit=ship-feature` — opens a kit (kit ids below)

Known kit ids: `ship-feature`, `decide`, `long-to-brief`, `explain-simply`,
`research-fast`. Add more in `prompts.py::KITS`.

> **Note:** the internal section id `news` is temporarily retained for the
> Tools tab to keep `?section=` deep-links stable. The next rename PR will
> move it to `tools`. Tracked as follow-up debt.

## Local development

```bash
git clone https://huggingface.co/spaces/vrobert94/ai-news
cd ai-news
python3 -m venv .venv
./.venv/bin/pip install -r requirements.txt
cp .env.example .env  # add GROQ_API_KEY for real summaries
./.venv/bin/streamlit run app.py
```

> macOS Apple Silicon: use `arch -arm64 ./.venv/bin/python3` for venv Python
> to avoid pydantic-core arch mismatch.

## Deployment

Pushed to both GitHub (`robert790/ai-news`) and Hugging Face Spaces
(`vrobert94/ai-news`). HF rebuild is automatic on push (~60s).

## More

- See **[HANDOFF.md](HANDOFF.md)** for full architecture, conventions,
  where this is going, and gotchas for continuing in another environment.
- See **[docs/LEARNING_TAB_PLAN.md](docs/LEARNING_TAB_PLAN.md)** for the
  learning tab design rationale.
- See **[DEPLOY.md](DEPLOY.md)** for HF Spaces deploy notes.

## License

MIT