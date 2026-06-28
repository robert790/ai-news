"""Streamlit UI for Ziarul Digital · v2.0.

Sidebar-first navigation. Always-visible nav lets users flip between
the three top-level sides — Learning, Jobs, News — plus Azi (default
daily brief) and Prompts (when the user's folder arrives).

  ☀️ Azi        — daily brief: top 3 from each + lesson + prompt
  📡 News       — full feeds from 6 sources
  📚 Learning   — AI Road course (v0.4 = RAG)
  💼 Jobs       — AI job feed + skill matching (v0.6)
  🛠 Prompts    — Prompt Bible (placeholder until folder is ready)

Design follows frontend-design-expert principles:
  - clarity: one nav, one section, one purpose per page
  - consistency: same card style, typography, color usage everywhere
  - efficiency: zero hunting — sidebar always visible
  - delight: subtle hover lift, gentle reveal animations

Run: streamlit run app.py
"""
import streamlit as st
from datetime import datetime
from zoneinfo import ZoneInfo
import sys
from pathlib import Path

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
from theme import render_css, COLORS, SECTION_ACCENT


# ===== Page config =====
st.set_page_config(
    page_title="Ziarul Digital",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(render_css(), unsafe_allow_html=True)


# ===== Data loaders (cached) =====
@st.cache_data(ttl=1800, show_spinner=False)
def load_hn():
    return fetch_hackernews_ai(limit=8)


@st.cache_data(ttl=3600, show_spinner=False)
def load_hf():
    return fetch_hf_papers(limit=8)


@st.cache_data(ttl=3600, show_spinner=False)
def load_repos():
    return fetch_findarepo_daily(limit=8)


@st.cache_data(ttl=3600, show_spinner=False)
def load_github():
    return fetch_github_trending(limit=8)


@st.cache_data(ttl=1800, show_spinner=False)
def load_lobsters():
    return fetch_lobsters(limit=8)


@st.cache_data(ttl=86400, show_spinner=False)
def load_importai():
    return fetch_importai(limit=5)


# ===== Helpers =====
def fmt_date(iso_str: str) -> str:
    if not iso_str:
        return ""
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        now = datetime.now(ZoneInfo("UTC"))
        delta = now - dt
        if delta.days == 0:
            hours = delta.seconds // 3600
            if hours == 0:
                mins = max(delta.seconds // 60, 1)
                return f"{mins}m ago"
            return f"{hours}h ago"
        if delta.days == 1:
            return "yesterday"
        if delta.days < 7:
            return f"{delta.days}d ago"
        return dt.strftime("%b %d")
    except (ValueError, AttributeError):
        return iso_str[:10] or ""


def section_header(title: str, caption: str):
    """Render the consistent section header. Used in every section."""
    st.markdown(
        f'<div class="section-header reveal-1">'
        f'<h1>{title}</h1>'
        f'<p class="caption">{caption}</p>'
        f'</div>',
        unsafe_allow_html=True,
    )


def subhead(label: str, color: str = "muted"):
    """Small uppercase label above content blocks. Optional accent color."""
    st.markdown(
        f'<div class="subsection-label reveal-1" style="color: var(--{color});">{label}</div>',
        unsafe_allow_html=True,
    )


# ===== Sidebar =====
now = datetime.now(ZoneInfo("Europe/Bucharest"))
date_short = now.strftime("%a %d %b").lower()
status_html = (
    '<span style="color: var(--sage);">● Groq connected</span>'
    if config.has_llm()
    else '<span style="color: var(--muted-2);">⚠ demo</span>'
)

with st.sidebar:
    st.markdown(
        f'<div class="sidebar-brand">'
        f'<h2>📡 Ziarul Digital</h2>'
        f'<p>Daily AI briefing</p>'
        f'</div>',
        unsafe_allow_html=True,
    )

    SECTION = st.radio(
        "Navigate",
        options=["azi", "news", "learning", "jobs", "prompts"],
        format_func={
            "azi":      "☀️  Azi",
            "news":     "📡  News",
            "learning": "📚  Learning",
            "jobs":     "💼  Jobs",
            "prompts":  "🛠  Prompts",
        }.get,
        index=0,
        label_visibility="hidden",
        key="section",
    )

    st.markdown(
        f'<div class="sidebar-meta">'
        f'<div>{date_short}</div>'
        f'<div style="margin-top: 0.3rem;">{status_html}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


# =====================================================================
# SECTION: AZI — daily brief
# =====================================================================
if SECTION == "azi":

    section_header(
        "Azi",
        "Top 3 din fiecare. Bea cafeaua, scanează lumea, pleci la treabă.",
    )

    subhead("Știri · Unelte · Joburi", "muted")

    col_news, col_tools, col_jobs = st.columns(3, gap="medium")

    with col_news:
        hn = load_hn()
        if hn:
            for i, item in enumerate(hn[:3]):
                with st.container(border=True):
                    st.markdown(
                        f'<div class="reveal reveal-{i+1}" style="color: var(--coral); '
                        f'font-family: JetBrains Mono, monospace; font-size: 0.68rem; '
                        f'letter-spacing: 0.06em; text-transform: uppercase; '
                        f'margin-bottom: 0.5rem;">📡 Știre #{i+1}</div>',
                        unsafe_allow_html=True,
                    )
                    st.markdown(f"**[{item.title[:90]}]({item.url})**")
                    summary = (item.summary or "")[:140]
                    if summary:
                        st.caption(summary + ("..." if len(item.summary or "") > 140 else ""))
                    st.caption(f"HackerNews · ⬆ {item.score} · {fmt_date(item.published_at)}")

    with col_tools:
        repos = load_repos()
        if repos:
            for i, r in enumerate(repos[:3]):
                with st.container(border=True):
                    st.markdown(
                        f'<div class="reveal reveal-{i+1}" style="color: var(--sky); '
                        f'font-family: JetBrains Mono, monospace; font-size: 0.68rem; '
                        f'letter-spacing: 0.06em; text-transform: uppercase; '
                        f'margin-bottom: 0.5rem;">⭐ Unealtă #{i+1}</div>',
                        unsafe_allow_html=True,
                    )
                    st.markdown(f"**[{r.full_name}]({r.url})**")
                    desc = (r.description or "")[:120]
                    if desc:
                        st.caption(desc + ("..." if len(r.description or "") > 120 else ""))
                    st.caption(f"findarepo · ★ {r.stars} · ↗ +{r.growth}/7d · `{r.language}`")

    with col_jobs:
        mock_jobs = [
            {"title": "LLM Engineer", "company": "DRUID AI", "location": "Bucharest", "match": "82%"},
            {"title": "AI Product Manager", "company": "Bitdefender", "location": "Bucharest", "match": "76%"},
            {"title": "AI Solutions Consultant", "company": "ClusterPower", "location": "Iași", "match": "71%"},
        ]
        for i, j in enumerate(mock_jobs):
            with st.container(border=True):
                st.markdown(
                    f'<div class="reveal reveal-{i+1}" style="color: var(--sage); '
                    f'font-family: JetBrains Mono, monospace; font-size: 0.68rem; '
                    f'letter-spacing: 0.06em; text-transform: uppercase; '
                    f'margin-bottom: 0.5rem;">💼 Job #{i+1}</div>',
                    unsafe_allow_html=True,
                )
                st.markdown(f"**{j['title']}**")
                st.caption(f"{j['company']} · 📍 {j['location']}")
                st.markdown(
                    f'<div style="font-family: Newsreader, serif; font-size: 1.7rem; '
                    f'color: var(--sage); margin-top: 0.3rem;">{j["match"]}</div>',
                    unsafe_allow_html=True,
                )
                st.caption("match score")
        st.caption("🚧 Live job feed vine în v0.6")

    st.markdown("<div style='height: 2.5rem;'></div>", unsafe_allow_html=True)

    col_lesson, col_prompt = st.columns(2, gap="medium")
    with col_lesson:
        subhead("📚 Lecția zilei", "sage")
        with st.container(border=True):
            st.markdown("### Ce este un LLM?")
            st.caption("Capitolul 3 · 5 minute · The AI Road")
            st.markdown(
                "Large Language Models sunt rețele neuronale antrenate pe cantități "
                "masive de text. Învață pattern-uri statistice care le permit să "
                "genereze text coerent, să răspundă la întrebări, și să raționeze "
                "într-o oarecare măsură."
            )
            st.markdown(
                '<a href="../ai-beginners-guide/index.html#chapter-3" target="_blank">'
                'Citește capitolul →</a>',
                unsafe_allow_html=True,
            )

    with col_prompt:
        subhead("🛠 Prompt de încercat", "lavender")
        with st.container(border=True):
            st.markdown("### Explică-mi ca și cum aș avea 12 ani")
            st.caption("Forțează LLM-ul să simplifice orice concept tehnic.")
            st.markdown(
                '<pre style="background: var(--surface-2); padding: 0.9rem; '
                'border-radius: 8px; margin: 0.8rem 0; font-family: JetBrains Mono, '
                'monospace; font-size: 0.8rem; color: var(--text-2); white-space: pre-wrap;">'
                'Explică [concept] ca și cum aș avea 12 ani. '
                'Folosește o analogie din viața de zi cu zi.</pre>',
                unsafe_allow_html=True,
            )
            st.caption("🚧 Prompt Bible completă vine cu folder-ul tău")


# =====================================================================
# SECTION: NEWS
# =====================================================================
elif SECTION == "news":

    section_header(
        "News",
        "Deep dive pe 6 surse: cercetare, comunitate, trenduri, analiză.",
    )

    subhead("🔬 Cercetare", "sky")
    papers = summarize_batch(load_hf()[:5])
    if papers:
        for p in papers:
            with st.container(border=True):
                st.markdown(f"[{p.title}]({p.url})")
                st.markdown(f"_{p.summary}_")
                meta = [f"⬆ {p.score}"]
                if p.author:
                    meta.append(f"👤 {p.author[:50]}")
                st.caption(" · ".join(meta))

    st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)

    subhead("💬 Comunitate", "coral")
    col_hn, col_lob = st.columns(2, gap="medium")
    with col_hn:
        st.caption("HackerNews")
        hn_items = summarize_batch(load_hn()[:5])
        if hn_items:
            for item in hn_items:
                with st.container(border=True):
                    st.markdown(f"[{item.title}]({item.url})")
                    st.caption(f"⬆ {item.score} · 👤 {item.author or 'anon'} · {fmt_date(item.published_at)}")

    with col_lob:
        st.caption("Lobsters")
        lob_items = summarize_batch(load_lobsters()[:5])
        if lob_items:
            for item in lob_items:
                with st.container(border=True):
                    st.markdown(f"[{item.title}]({item.url})")
                    st.caption(f"⬆ {item.score} · 👤 {item.author or 'anon'} · {fmt_date(item.published_at)}")

    st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)

    subhead("⭐ Trenduri GitHub", "lavender")
    col_fr, col_gh = st.columns(2, gap="medium")
    with col_fr:
        st.caption("findarepo · 7-day growth")
        repos = load_repos()[:5]
        if repos:
            for r in repos:
                with st.container(border=True):
                    st.markdown(f"[{r.full_name}]({r.url})")
                    st.caption(f"★ {r.stars} · ↗ +{r.growth}/7d · `{r.language}`")

    with col_gh:
        st.caption("GitHub Trending · today")
        gh_items = load_github()[:5]
        if gh_items:
            for it in gh_items:
                with st.container(border=True):
                    st.markdown(f"[{it.title}]({it.url})")
                    tags_short = "/".join(t for t in it.tags if t not in ("github", "repo", "trending")) or "—"
                    st.caption(f"⬆ {it.score} stars today · `{tags_short}`")

    st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)

    subhead("📰 Analiză săptămânală", "coral")
    ai_items = summarize_batch(load_importai()[:3])
    if ai_items:
        for it in ai_items:
            with st.container(border=True):
                st.markdown(f"[{it.title}]({it.url})")
                st.markdown(f"_{it.summary}_")
                st.caption(f"📝 {it.author} · {fmt_date(it.published_at)}")


# =====================================================================
# SECTION: LEARNING
# =====================================================================
elif SECTION == "learning":

    section_header(
        "Learning",
        "Cursul complet. De la zero la product-ready AI.",
    )

    with st.container(border=True):
        st.markdown("### The AI Road")
        st.markdown(
            "Un ghid practic care te duce de la zero la product-ready. "
            "Fiecare capitol leagă teoria de ce se întâmplă azi în știri."
        )
        st.markdown(
            "În v0.4, fiecare capitol va fi queryabil prin RAG — "
            "pui o întrebare, primești context + legătură directă la capitol."
        )
        st.markdown(
            '<a href="../ai-beginners-guide/index.html" target="_blank">'
            '→ Deschide cursul complet</a>',
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)

    st.markdown("#### Cuprins")
    st.caption("Cele 15 capitole ale cursului.")

    chapters = [
        ("1",  "Ce este AI-ul astăzi", "MIT, hype, realitate"),
        ("2",  "Machine learning în 10 minute", "Supervised, unsupervised, reinforcement"),
        ("3",  "Ce este un LLM", "Transformers, tokenizare, atenție"),
        ("4",  "Cum antrenezi un model", "Pre-training, fine-tuning, RLHF"),
        ("5",  "RAG — retrieval augmented generation", "Cum adaugi cunoștințe externe LLM-ului"),
        ("6",  "Fine-tuning și adapters", "LoRA, QLoRA, PEFT"),
        ("7",  "Agenți și tool use", "Când LLM-ul încetează să fie doar chatbot"),
        ("8",  "Evaluare și metrici", "Cum știi dacă modelul tău e bun"),
        ("9",  "Producție și cost", "Inference, latency, token economics"),
        ("10", "Safety și alignment", "Ce poate merge prost, cum reduci riscurile"),
    ]
    for num, title, blurb in chapters:
        with st.container(border=True):
            cols = st.columns([1, 6])
            with cols[0]:
                st.markdown(
                    f'<div style="font-family: Newsreader, serif; font-size: 1.8rem; '
                    f'color: var(--sage); line-height: 1;">{num}</div>',
                    unsafe_allow_html=True,
                )
            with cols[1]:
                st.markdown(f"**{title}**")
                st.caption(blurb)


# =====================================================================
# SECTION: JOBS
# =====================================================================
elif SECTION == "jobs":

    section_header(
        "Jobs",
        "Joburi AI care se potrivesc cu ce înveți. Skill matching LLM-powered.",
    )

    with st.container(border=True):
        st.markdown("### 🚧 În construcție")
        st.markdown(
            "Live job feed vine în v0.6. Intenția: scrape LinkedIn, Indeed, "
            "și platforme românești (BestJobs, eJobs); extrage skill-uri cu LLM; "
            "match-ează cu profilul tău; sugerează capitole din The AI Road "
            "pentru skill gaps."
        )

    st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)

    st.markdown("#### Preview · mock data")
    st.caption("Demo cu 3 joburi ca să vezi layout-ul final.")

    mock_jobs_full = [
        {"title": "LLM Engineer", "company": "DRUID AI", "location": "Bucharest", "match": "82%", "skills_gap": "LangChain, Vector DBs"},
        {"title": "AI Product Manager", "company": "Bitdefender", "location": "Bucharest", "match": "76%", "skills_gap": "Eval, RAG"},
        {"title": "AI Solutions Consultant", "company": "ClusterPower", "location": "Iași", "match": "71%", "skills_gap": "GPU infrastructure"},
        {"title": "ML Engineer", "company": "UiPath", "location": "Bucharest", "match": "68%", "skills_gap": "Fine-tuning, RLHF"},
    ]
    for j in mock_jobs_full:
        with st.container(border=True):
            cols = st.columns([5, 1])
            with cols[0]:
                st.markdown(f"**{j['title']}** · {j['company']}")
                st.caption(f"📍 {j['location']} · Skills gap: {j['skills_gap']}")
            with cols[1]:
                st.markdown(
                    f'<div style="font-family: Newsreader, serif; font-size: 1.7rem; '
                    f'color: var(--sage); text-align: right;">{j["match"]}</div>',
                    unsafe_allow_html=True,
                )


# =====================================================================
# SECTION: PROMPTS
# =====================================================================
elif SECTION == "prompts":

    section_header(
        "Prompts",
        "Prompturi gata de folosit. Copiază, lipește, rezolvă.",
    )

    with st.container(border=True):
        st.markdown("### Prompt Bible")
        st.markdown(
            '<p style="color: var(--lavender); font-family: JetBrains Mono, monospace; '
            'font-size: 0.7rem; letter-spacing: 0.06em; text-transform: uppercase; '
            'margin: 0.5rem 0 1rem;">🚧 În construcție</p>',
            unsafe_allow_html=True,
        )
        st.markdown(
            "Mii de prompturi organizate pe categorii — coding, writing, research, "
            "brainstorming, debugging, documentare. Cu search, tags, și exemplu "
            "de output pentru fiecare."
        )
        st.markdown(
            '<p style="color: var(--muted); margin-top: 1rem; font-style: italic;">'
            "Când folder-ul cu prompturi e gata, le integrăm aici. "
            "Până atunci, încearcă starter pack-ul de mai jos."
            "</p>",
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)

    st.markdown("#### Starter pack")
    st.caption("Câteva prompturi ca să vezi vibe-ul.")

    starter_prompts = [
        {
            "title": "Explained like I'm 12",
            "category": "Learning",
            "prompt": "Explică [concept] ca și cum aș avea 12 ani. Folosește o analogie din viața de zi cu zi.",
        },
        {
            "title": "Code review blând",
            "category": "Coding",
            "prompt": "Review this code as a senior engineer who's kind, specific, and prioritizes clarity over cleverness. Point out 3 things to improve, 1 thing done well.",
        },
        {
            "title": "Decision framework",
            "category": "Strategy",
            "prompt": "I'm deciding between [A] and [B]. Ask me 5 clarifying questions first, then give a recommendation with reasoning.",
        },
        {
            "title": "Bug autopsy",
            "category": "Debugging",
            "prompt": "Help me understand why this code fails. Walk through it line by line, identify the root cause, and suggest 2 fixes with trade-offs.",
        },
    ]
    for p in starter_prompts:
        with st.container(border=True):
            st.markdown(f"**{p['title']}**")
            st.caption(
                f'<span style="color: var(--lavender); font-family: JetBrains Mono, '
                f'monospace; font-size: 0.7rem; letter-spacing: 0.04em;">'
                f'{p["category"].upper()}</span>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<pre style="background: var(--surface-2); padding: 0.8rem; '
                f'border-radius: 8px; margin: 0.7rem 0 0; font-family: JetBrains Mono, '
                f'monospace; font-size: 0.8rem; color: var(--text-2); white-space: pre-wrap;">'
                f'{p["prompt"]}</pre>',
                unsafe_allow_html=True,
            )


# ===== Footer =====
st.markdown(
    '<div style="border-top: 1px solid var(--border); padding-top: 1.5rem; margin-top: 4rem; '
    'font-family: JetBrains Mono, monospace; font-size: 0.7rem; '
    'color: var(--muted-2); text-align: center; letter-spacing: 0.04em;">'
    'Ziarul Digital · v2.0 · pentru ingineri care beau cafeaua cu ochii pe lume'
    '</div>',
    unsafe_allow_html=True,
)