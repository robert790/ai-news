"""Streamlit UI for Ziarul Digital · v0.3.

The relaxed engineering workspace. Three tabs:
  1. 📰 News AI    — daily AI research + discussions + repos + analysis
                     (HuggingFace Papers · HackerNews · Lobsters ·
                      findarepo · GitHub Trending · Import AI)
  2. 🎓 Learning   — AI learning path (placeholder for v0.4 RAG module)
  3. 💼 Jobs       — AI job transition helper (placeholder for v0.6)

Run: streamlit run app.py
"""
import streamlit as st
from datetime import datetime
import sys
from pathlib import Path

# Make project root importable
sys.path.insert(0, str(Path(__file__).parent))

from scrapers import (
    fetch_hackernews_ai,
    fetch_findarepo_daily,
    fetch_hf_papers,
    fetch_lobsters,
    fetch_github_trending,
    fetch_importai,
)
from llm import summarize_batch
from llm.summarizer import summarize
import config


# ===== Page config =====
st.set_page_config(
    page_title="Ziarul Digital",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ===== Custom CSS — relaxed dark workspace =====
st.markdown("""
<style>
  /* Dark workspace palette · warm, not corporate */
  .stApp { background-color: #1a1815; color: #e8e3d8; }
  section.main > div { padding-top: 2rem; }

  /* Tabs */
  .stTabs [data-baseweb="tab-list"] {
    gap: 0.5rem;
    background-color: transparent;
    border-bottom: 1px solid #3a3530;
  }
  .stTabs [data-baseweb="tab"] {
    background-color: transparent;
    color: #8a8478;
    padding: 0.75rem 1.25rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 13px;
    letter-spacing: 0.04em;
  }
  .stTabs [aria-selected="true"] {
    color: #d4a574 !important;
    border-bottom: 2px solid #d4a574 !important;
  }

  /* Headings */
  h1 { color: #f4ede0 !important; font-weight: 300 !important; }
  h2 { color: #e8e3d8 !important; font-weight: 400 !important; }
  h3 { color: #d4a574 !important; font-weight: 500 !important; }
  p, li, span, div { color: #c4bdb0; }

  /* Caption + small text */
  .stCaption, [data-testid="stCaption"] { color: #8a8478 !important; }

  /* Cards (containers with borders) */
  [data-testid="stVerticalBlockBorderWrapper"] {
    background-color: #242019;
    border: 1px solid #3a3530 !important;
    border-radius: 12px !important;
    padding: 1rem 1.25rem !important;
  }

  /* Buttons */
  .stButton > button {
    background-color: transparent;
    color: #d4a574;
    border: 1px solid #3a3530;
    border-radius: 8px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    transition: all .15s;
  }
  .stButton > button:hover {
    background-color: #2f2a23;
    border-color: #d4a574;
  }

  /* Markdown links */
  a { color: #d4a574 !important; }
  a:hover { color: #e8b889 !important; }

  /* Code blocks */
  code {
    background-color: #2f2a23 !important;
    color: #d4a574 !important;
    font-family: 'JetBrains Mono', monospace !important;
  }
</style>
""", unsafe_allow_html=True)


# ===== Header =====
col_title, col_status = st.columns([3, 1])
with col_title:
    st.markdown("# 📡 Ziarul Digital")
    st.markdown("*Daily AI for engineers. Sip your coffee, scan the world.*")
with col_status:
    st.markdown(f"`{datetime.now().strftime('%a %d %b · %H:%M')}`")
    if not config.has_deepseek():
        st.caption("⚠ demo mode · add DEEPSEEK_API_KEY")
    else:
        st.caption("✓ DeepSeek connected")


# ===== DEBUG BLOCK (temporary — helps diagnose env var pickup) =====
with st.expander("🔧 Debug · env state", expanded=False):
    import os
    raw_key = os.getenv("DEEPSEEK_API_KEY", "")
    all_deep = {k: ("*" * min(len(v), 8) + f" ({len(v)} chars)" if v else "∅")
                for k, v in os.environ.items()
                if "DEEP" in k.upper() or "deepseek" in k.lower()}
    if all_deep:
        env_dump = "\n  ".join(f"{k}: {v}" for k, v in all_deep.items())
    else:
        env_dump = "(none)"
    st.code(
        f"DEEPSEEK_API_KEY length : {len(raw_key)}\n"
        f"DEEPSEEK_API_KEY prefix : {raw_key[:7]!r}\n"
        f"has_deepseek()          : {config.has_deepseek()}\n"
        f"All env vars with DEEP/deepseek:\n  {env_dump}",
        language="text",
    )


# ===== Tabs =====
tab_news, tab_learn, tab_jobs = st.tabs(["📰 NEWS AI", "🎓 AI LEARNING PATH", "💼 AI JOB TRANSITION"])


# =====================================================================
# TAB 1: NEWS AI
# =====================================================================
with tab_news:

    st.markdown("### What's new today")
    st.caption("Romanian summaries · global sources · daily updated")

    # -----------------------------------------------------------------
    # Section 1 · Today's Research · HuggingFace Daily Papers
    # -----------------------------------------------------------------
    st.markdown("")
    st.markdown("#### 🔬 Today's Research")
    st.caption("Top papers trending on HuggingFace")

    @st.cache_data(ttl=3600, show_spinner="Se încarcă cercetarea...")
    def load_research():
        return fetch_hf_papers(limit=5)

    with st.spinner(""):
        papers = summarize_batch(load_research())

    if not papers:
        st.warning("Nu s-au putut încărca lucrări de pe HuggingFace.")
    else:
        for p in papers:
            with st.container(border=True):
                cols = st.columns([6, 1])
                with cols[0]:
                    st.markdown(f"##### [{p.title}]({p.url})")
                    st.markdown(f"_{p.summary}_")
                    meta_bits = [f"📄 HF Papers", f"⬆ {p.score}"]
                    if p.author:
                        meta_bits.append(f"👤 {p.author[:40]}")
                    st.caption(" · ".join(meta_bits))
                with cols[1]:
                    if config.PREMIUM_ENABLED:
                        st.button("🔍 Explică", key=f"paper-{p.external_id}", use_container_width=True)
                    else:
                        st.button("🔒", key=f"paper-lock-{p.external_id}", disabled=True, use_container_width=True)

    # -----------------------------------------------------------------
    # Section 2 · Community Buzz · HackerNews + Lobsters side-by-side
    # -----------------------------------------------------------------
    st.markdown("")
    st.markdown("#### 💬 Community Buzz")
    st.caption("What the dev community is talking about")

    col_hn, col_lob = st.columns(2)

    @st.cache_data(ttl=1800, show_spinner="Se încarcă discuțiile...")
    def load_hn():
        return summarize_batch(fetch_hackernews_ai(limit=6))

    @st.cache_data(ttl=1800, show_spinner="Se încarcă Lobsters...")
    def load_lobsters():
        return summarize_batch(fetch_lobsters(limit=6))

    with col_hn:
        st.markdown("**🔥 HackerNews**")
        with st.spinner(""):
            hn_items = load_hn()
        if not hn_items:
            st.caption("Nu s-au putut încărca știri HN.")
        for item in hn_items:
            with st.container(border=True):
                st.markdown(f"[{item.title}]({item.url})")
                st.caption(f"⬆ {item.score} · 👤 {item.author or 'anon'}")

    with col_lob:
        st.markdown("**🦞 Lobsters**")
        with st.spinner(""):
            lob_items = load_lobsters()
        if not lob_items:
            st.caption("Nu s-au putut încărca povești Lobsters.")
        for item in lob_items:
            with st.container(border=True):
                st.markdown(f"[{item.title}]({item.url})")
                st.caption(f"⬆ {item.score} · 👤 {item.author or 'anon'}")

    # -----------------------------------------------------------------
    # Section 3 · Trending Repos · findarepo + GitHub Trending
    # -----------------------------------------------------------------
    st.markdown("")
    st.markdown("#### ⭐ Trending Repos")
    st.caption("Hottest GitHub repos right now")

    col_fr, col_gh = st.columns(2)

    @st.cache_data(ttl=3600, show_spinner="Se încarcă findarepo...")
    def load_repos():
        return fetch_findarepo_daily(limit=6)

    @st.cache_data(ttl=3600, show_spinner="Se încarcă GitHub Trending...")
    def load_gh_trending():
        return fetch_github_trending(limit=6)

    with col_fr:
        st.markdown("**📊 findarepo (7-day growth)**")
        with st.spinner(""):
            repos = load_repos()
        if not repos:
            st.caption("Nu s-au putut încărca repo-uri findarepo.")
        for r in repos:
            with st.container(border=True):
                st.markdown(f"[{r.full_name}]({r.url})")
                st.caption(f"★ {r.stars} total · ↗ +{r.growth}/7d · `{r.language}`")

    with col_gh:
        st.markdown("**🔥 GitHub Trending (today)**")
        with st.spinner(""):
            gh_items = load_gh_trending()
        if not gh_items:
            st.caption("Nu s-au putut încărca repo-uri GitHub Trending.")
        for it in gh_items:
            with st.container(border=True):
                st.markdown(f"[{it.title}]({it.url})")
                tags_short = "/".join(t for t in it.tags if t not in ("github", "repo", "trending")) or "—"
                st.caption(f"⬆ {it.score} stars today · `{tags_short}`")

    # -----------------------------------------------------------------
    # Section 4 · Weekly Analysis · Import AI
    # -----------------------------------------------------------------
    st.markdown("")
    st.markdown("#### 📰 Deep Analysis")
    st.caption("Weekly essays from Jack Clark's Import AI")

    @st.cache_data(ttl=86400, show_spinner="Se încarcă Import AI...")
    def load_importai():
        return summarize_batch(fetch_importai(limit=3))

    with st.spinner(""):
        ai_items = load_importai()

    if not ai_items:
        st.warning("Nu s-au putut încărca articole Import AI.")
    else:
        for it in ai_items:
            with st.container(border=True):
                cols = st.columns([6, 1])
                with cols[0]:
                    st.markdown(f"##### [{it.title}]({it.url})")
                    st.markdown(f"_{it.summary}_")
                    st.caption(f"📝 {it.author} · {it.published_at[:10]}")
                with cols[1]:
                    st.button("📖 Citește", key=f"ai-{it.external_id}", use_container_width=True)


# =====================================================================
# TAB 2: AI LEARNING PATH (placeholder for v0.4)
# =====================================================================
with tab_learn:

    st.markdown("### 🎓 AI Learning Path")
    st.caption("Learn what's behind today's news · powered by The AI Road curriculum")

    st.markdown("")

    # Show 3 example starting paths
    col_a, col_b, col_c = st.columns(3)

    with col_a:
        with st.container(border=True):
            st.markdown("##### 🟢 Beginner")
            st.markdown("Start from zero")
            st.caption("What neural networks are, how to talk to AI, reading your first paper.")
            st.button("Start", key="learn-beg", use_container_width=True)

    with col_b:
        with st.container(border=True):
            st.markdown("##### 🟡 Intermediate")
            st.markdown("You know the basics")
            st.caption("Build your first RAG app, fine-tune a model, deploy an agent.")
            st.button("Start", key="learn-int", use_container_width=True)

    with col_c:
        with st.container(border=True):
            st.markdown("##### 🔴 Advanced")
            st.markdown("Ship things in production")
            st.caption("Eval harnesses, observability, multi-agent systems, frontier awareness.")
            st.button("Start", key="learn-adv", use_container_width=True)

    st.markdown("")
    st.info("🚧 **Coming in v0.4** — Adaptive learning that links each chapter to today's news. Your progress syncs across devices.")

    # Quick link to the full course
    st.markdown("")
    st.markdown("**📖 Full course available now:** [The AI Road](../ai-beginners-guide/index.html) — 15 chapters, glossary, resources.")


# =====================================================================
# TAB 3: AI JOB TRANSITION HELPER (placeholder for v0.6)
# =====================================================================
with tab_jobs:

    st.markdown("### 💼 AI Job Transition Helper")
    st.caption("Find jobs that match what you're learning · identify skill gaps")

    st.markdown("")

    # Mock filters for the UI
    col_filter1, col_filter2, col_filter3 = st.columns(3)

    with col_filter1:
        st.markdown("**Your current skills**")
        st.multiselect(
            "What do you know?",
            ["Python", "JavaScript", "Prompting", "LangChain", "RAG", "Fine-tuning", "PyTorch", "Vector DBs"],
            default=["Prompting"],
            key="job-skills",
        )

    with col_filter2:
        st.markdown("**Your target role**")
        st.selectbox(
            "Where do you want to be?",
            ["LLM Engineer", "AI Product Manager", "AI Solutions Architect", "ML Engineer", "AI Consultant"],
            key="job-role",
        )

    with col_filter3:
        st.markdown("**Location**")
        st.selectbox(
            "Where?",
            ["Remote (EU)", "Bucharest", "Romania", "Berlin", "London", "Anywhere"],
            key="job-loc",
        )

    st.markdown("")

    # Mock results preview
    st.markdown("#### 🎯 Matches for you")
    st.caption("3 jobs · last refreshed 2h ago")

    mock_jobs = [
        {"title": "LLM Engineer", "company": "DRUID AI", "location": "Bucharest", "match": "82%", "skills_gap": "LangChain, Vector DBs"},
        {"title": "AI Product Manager", "company": "Bitdefender", "location": "Bucharest", "match": "76%", "skills_gap": "Eval, RAG"},
        {"title": "AI Solutions Consultant", "company": "ClusterPower", "location": "Iași", "match": "71%", "skills_gap": "GPU infrastructure"},
    ]

    for j in mock_jobs:
        with st.container(border=True):
            cols = st.columns([5, 1])
            with cols[0]:
                st.markdown(f"##### {j['title']} · {j['company']}")
                st.caption(f"📍 {j['location']} · Skills gap: {j['skills_gap']}")
            with cols[1]:
                st.markdown(f"### {j['match']}")
                st.caption("match score")

    st.markdown("")
    st.info("🚧 **Coming in v0.6** — Live job feed from LinkedIn, Indeed, and Romanian platforms. Real skill matching with LLM extraction. Personalized learning paths to close gaps.")


# ===== Footer =====
st.markdown("")
st.markdown("---")
st.caption("Ziarul Digital · v0.3 · built for engineers who sip coffee · sources: HuggingFace Papers, HackerNews, Lobsters, findarepo, GitHub Trending, Import AI")