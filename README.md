---
title: OpenRadar · Ziarul Digital
emoji: 📡
colorFrom: green
colorTo: yellow
sdk: streamlit
sdk_version: 1.32.0
app_file: app.py
pinned: false
license: mit
short_description: Romanian-first AI radar · news + learning + jobs
---

# 📡 OpenRadar

Romanian-first AI radar for builders. Scan news, walk a 10-chapter curriculum, match jobs, copy prompts.

- **Groq** ☀ — daily AI briefing in Romanian
- **News** ◌ — Hacker News AI stories, Groq-summarized in Romanian (deterministic fallback when no key is set)
- **Learning** ❡ — 10-chapter category walkthrough: history → LLMs → vision → diffusion → speech → RAG → agents → build → apply
- **Jobs** ◆ — skill-gap matcher between your CV and AI infra roles (Romania focus)
- **Prompts** ✦ — curated prompt library with copy buttons

## How it works

The app fetches AI-related stories from Hacker News and trending repos from
findarepo.com, summarizes via Groq (OpenAI-compatible, free tier, Romanian-first
prompts), with a deterministic fallback when no key is set. The interface is
a warm-dark workspace with sage/amber/coral accents. Learning is offline
content — 10 chapters with methods, verifiers, and a curator persona (Groq).

## Deep links

- `/` — Groq (default landing)
- `/?section=learning&ch=ch1` — opens chapter 1 directly
- `/?section=news`, `?section=jobs`, `?section=prompts`

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