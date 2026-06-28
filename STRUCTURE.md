# Project structure

```
/Users/zero/.minimax-agent/projects/ai-news/
├── README.md              ← project vision, roadmap, sources
├── app.py                 ← Streamlit UI · 3 tabs · dark workspace theme
├── config.py              ← env vars, model names, paths
├── requirements.txt       ← Python deps
├── .env.example           ← template (copy → .env, add DEEPSEEK_API_KEY)
├── .gitignore             ← ignores venv, .env, data/cache
├── docs/
│   └── decisions.md       ← the "why" log for every major choice
├── scrapers/
│   ├── __init__.py        ← exports both fetch_* functions
│   ├── hackernews.py      ← HN Algolia API · no key required
│   └── findarepo.py       ← findarepo.com · daily top 10 repos by 7d growth
├── llm/
│   ├── __init__.py        ← exports summarize, summarize_batch
│   └── summarizer.py      ← DeepSeek → Romanian summaries + demo fallback
├── rag/                   ← empty · premium tier goes here v0.4
├── jobs/                  ← empty · jobs module goes here v0.6
├── data/                  ← runtime cache, vector store
├── tests/                 ← empty · eval harness goes here v0.5
└── .venv/                 ← Python virtualenv (gitignored, ~1.1GB)
```

## Git history

```
7adabe6 v0.2: 3-tab workspace + findarepo trending repos
3711b52 v0.1: scaffold AI News app with HN scraper + Romanian summaries
```

## How to run

```bash
cd /Users/zero/.minimax-agent/projects/ai-news
source .venv/bin/activate
streamlit run app.py
# Opens at http://localhost:8501
```

Without DEEPSEEK_API_KEY in `.env`, summaries fall back to templates (still works).
