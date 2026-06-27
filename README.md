# Ziarul Digital · AI News + Learning + Jobs

> Romanian-first AI platform: read today's news, learn what's behind it, see which jobs need the skill. Three reasons to come back, one product.

## What this is

A vertical AI product that fills a gap nobody in Europe owns yet: **Romanian-language AI news, with personalized learning and job matching**. The news feed is the entry point. The learning is the value. The jobs are the outcome.

### Three modules

| Module | What it does | Status |
|---|---|---|
| **📰 News Feed** | Romanian summaries of global + local AI news | v0.1 built |
| **🎓 Learn** | "Explain this story" with AI Road context · "What should I learn next?" | v0.4 (next) |
| **💼 Jobs** | Aggregated AI jobs + skill matching | v0.6 |

### The user flow

```
Read news story (Romanian, 2-3 sentences)
  ↓ "I want to understand this better"
Deep dive · pulls relevant AI Road chapter via RAG
  ↓ "What jobs need this skill?"
Job board filtered by what you've learned
```

One product. Three reasons to return.

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
- [ ] **v0.2** — Add HF papers + 1 Romanian tech source
- [ ] **v0.3** — Relevance filter (Romania/EU/global)
- [ ] **v0.4** — Learn module · Chroma + RAG over AI Road
- [ ] **v0.5** — Eval harness (summary accuracy, deep-dive quality)
- [ ] **v0.6** — Jobs module · aggregator + skill matching
- [ ] **v1.0** — Deploy to HF Spaces, custom domain, auth, free vs paid tier
- [ ] **v2.0 (much later)** — NFC card access for premium (Ziarul Digital physical edition)

## Related

- Course: [The AI Road](../ai-beginners-guide/index.html) — the curriculum that powers the Learn module
- Portfolio context: This project is portfolio project #4 (deployed app) + #5 (eval suite) from AI Road Ch 12

## Status

Building. v0.1 done. Refocused from "news + NFC" to "news + learn + jobs" on 2026-06-27.

## Built by

A person learning AI by shipping. Course materials by Mavis.