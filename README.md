# Ziarul Digital · AI News + Learning + Jobs

> Romanian-first AI platform: read today's news, learn what's behind it, see which jobs need the skill. Three reasons to come back, one product.

## What this is

A relaxed engineering workspace for staying current with AI: read today's news, see what's trending on GitHub, learn what's behind the stories, find jobs that match your skills. One product, three tabs, coffee-friendly.

### Three modules (three tabs)

| Tab | What it does | Status |
|---|---|---|
| **📰 News AI** | Daily AI stories + trending GitHub repos, Romanian summaries | v0.2 built |
| **🎓 AI Learning Path** | Beginner → Intermediate → Advanced paths, links to AI Road | v0.4 (next) |
| **💼 AI Job Transition** | Skill-gap matching, mock jobs, will be live in v0.6 | v0.6 |

### The user flow

```
Open app → News tab → scan stories + trending repos
  ↓ "I want to understand this better"
Learning tab → pick level → see relevant AI Road chapter
  ↓ "What jobs need this skill?"
Jobs tab → see matches → see skill gap → back to Learning to close it
```

### Sources

- **Hacker News** — AI-tagged stories, scored by community
- **findarepo.com** — daily top 10 GitHub repos by 7-day star growth (measured, not estimated)
- Hugging Face papers, Import AI, The Batch, OECD AI, Romanian tech press — coming in v0.3

## Why this wins

- **No Romanian-language AI news exists today.** The wedge.
- **Personalized learning is the moat** — we adapt to the user's level, not generic.
- **Job matching closes the loop** — learning → earning is the most powerful narrative in tech education.
- **Built on real research** — sources from AI Road Ch 10-11 (OECD AI, McKinsey, Forbes AI 50, Romanian tech press).

## Architecture

```
ai-news/
├── scrapers/       # Source-specific scrapers (HN, HF papers, RSS)
├── llm/            # LLM calls (summarization, filtering, matching)
├── rag/            # Learn module · Chroma + AI Road content
├── jobs/           # Jobs module · scraper + matcher
├── data/           # Cached news, embeddings, vector store, jobs cache
├── tests/          # Unit tests + eval harness
├── docs/           # Project notes, decisions
├── app.py          # Streamlit UI (entry point)
├── config.py       # Config + secrets
└── README.md
```

## Tech stack

| Layer | Choice | Why |
|---|---|---|
| Language | Python 3.11+ | AI ecosystem standard |
| UI | Streamlit | Fast to build, looks clean |
| LLM | DeepSeek (news), Claude (deep dive) | Cheap + smart |
| Vector DB | Chroma | Free, runs locally |
| Scraping | httpx + feedparser | Modern, simple |
| Source code | GitHub | Portfolio-friendly |
| Hosting | Hugging Face Spaces (free) → Vercel later | Zero cost until PMF |

## Quick start

```bash
cd ~/projects/ai-news
source .venv/bin/activate            # venv already set up
pip install -r requirements.txt
cp .env.example .env                  # add DEEPSEEK_API_KEY for real summaries
streamlit run app.py                  # http://localhost:8501
```

## Roadmap

- [x] **v0.1** — HN scraper + Romanian summary + Streamlit UI
- [x] **v0.2** — 3-tab workspace · News + Learning + Jobs · findarepo trending repos
- [ ] **v0.3** — Add HF papers, Import AI, The Batch as News sources
- [ ] **v0.4** — Learn module · Chroma + RAG over AI Road
- [ ] **v0.5** — Eval harness (summary accuracy, deep-dive quality)
- [ ] **v0.6** — Jobs module · live aggregator + skill matching
- [ ] **v1.0** — Deploy to HF Spaces, custom domain, auth, free vs paid tier
- [ ] **v2.0 (much later)** — NFC card access for premium (Ziarul Digital physical edition)

## Related

- Course: [The AI Road](../ai-beginners-guide/index.html) — the curriculum that powers the Learn module
- Portfolio context: This project is portfolio project #4 (deployed app) + #5 (eval suite) from AI Road Ch 12

## Status

Building. v0.1 done. Refocused from "news + NFC" to "news + learn + jobs" on 2026-06-27.

## Built by

A person learning AI by shipping. Course materials by Mavis.