---
title: Ziarul Digital
emoji: 📡
colorFrom: green
colorTo: yellow
sdk: streamlit
sdk_version: 1.32.0
app_file: app.py
pinned: false
license: mit
short_description: Romanian-first AI news + trending repos for engineers
---

# 📡 Ziarul Digital

Daily AI for engineers. Sip your coffee, scan the world.

- **News AI** — Hacker News AI stories, summarized in Romanian
- **Trending repos** — findarepo.com daily top 10 by 7-day star growth
- **AI Learning Path** — coming soon (RAG over The AI Road curriculum)
- **AI Job Transition** — coming soon (skill-gap matching)

## How it works

The app fetches AI-related stories from Hacker News and trending repos from findarepo.com, summarizes everything via DeepSeek (with a deterministic fallback when no API key is set), and renders it as a relaxed dark workspace.

## Sources

- [Hacker News](https://news.ycombinator.com) via the public Algolia Search API
- [findarepo.com](https://findarepo.com) — daily top GitHub repos by measured 7-day star growth

## Local development

```bash
git clone https://huggingface.co/spaces/zero/ziarul-digital
cd ziarul-digital
pip install -r requirements.txt
cp .env.example .env  # add your DEEPSEEK_API_KEY for real summaries
streamlit run app.py
```

## License

MIT