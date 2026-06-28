"""Streamlit UI for Ziarul Digital · v1.1.

Single scrolling page. No tabs. Every section visible at a glance.

Layout (top to bottom):
  1. Header — name, tagline, date, status
  2. AZI       — top 3 from news/tools/jobs + today's lesson + today's prompt
  3. STIRI     — full feeds from 6 sources, organized by category
  4. INVATA    — AI Road course hero + chapter list
  5. APLICĂ    — Prompt Bible hero + starter pack

Frontier-model feel: generous spacing, calm typography, one section
at a time, never crowded. Each section is a clear module with a
distinct purpose — no hunting through tabs.

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
from theme import render_css, COLORS


# ===== Page config =====
st.set_page_config(
    page_title="Ziarul Digital",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(render_css(), unsafe_allow_html=True)


# ===== Helpers =====
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


def fmt_date(iso_str: str) -> str:
    """Render ISO timestamp as relative time ('2h ago' / 'yesterday' / '3d ago')."""
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


def section_header(emoji: str, title: str, subtitle: str, accent: str):
    """Render a section header block with anchor id + caption."""
    st.markdown(
        f'<a id="sec-{title.lower().replace(" ", "-")}"></a>'
        f'<div style="margin-top: 4rem; margin-bottom: 0.5rem;">'
        f'<span style="font-size: 2.2rem; margin-right: 0.6rem;">{emoji}</span>'
        f'<span style="font-family: Newsreader, serif; font-size: 2rem; font-weight: 400; '
        f'color: var(--text); letter-spacing: -0.01em;">{title}</span>'
        f'</div>'
        f'<p style="font-family: Newsreader, serif; font-style: italic; color: var(--muted); '
        f'margin: 0.25rem 0 1.5rem; padding-left: 2.8rem; font-size: 1.05rem;">'
        f'{subtitle}</p>'
        f'<div style="height: 1px; background: var(--border); '
        f'margin: 1.5rem 0 2rem;"></div>',
        unsafe_allow_html=True,
    )


# =====================================================================
# HEADER
# =====================================================================
now = datetime.now(ZoneInfo("Europe/Bucharest"))
date_str = now.strftime("%A · %d %B").lower()
status_html = (
    f'<span style="color: var(--sage);"><span class="pulse-dot"></span>Groq connected</span>'
    if config.has_llm()
    else '<span style="color: var(--muted-2);">⚠ demo mode</span>'
)

st.markdown(
    f"""
    <div style="margin: 1rem 0 2rem;">
      <h1 style="margin-bottom: 0.5rem; font-size: 2.5rem;">📡 Ziarul Digital</h1>
      <p style="font-family: Newsreader, serif; font-style: italic; color: var(--text-2);
                font-size: 1.15rem; margin: 0;">
        Every morning, your AI briefing in 60 seconds.
      </p>
      <div style="margin-top: 1rem; font-family: JetBrains Mono, monospace;
                  font-size: 0.78rem; color: var(--muted); letter-spacing: 0.03em;">
        ☀️ {date_str} &nbsp;·&nbsp; {status_html}
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# =====================================================================
# SECTION 1: AZI — morning glance
# =====================================================================
section_header(
    "☀️",
    "Azi",
    "Top 3 din fiecare. Citești, bei cafeaua, pleci la treabă.",
    "sage",
)

st.markdown(
    '<p style="font-family: JetBrains Mono, monospace; font-size: 0.72rem; '
    'color: var(--muted); letter-spacing: 0.06em; text-transform: uppercase; '
    'margin: 0 0 1.2rem;">'
    'Știri · Unelte · Joburi</p>',
    unsafe_allow_html=True,
)

col_news, col_tools, col_jobs = st.columns(3, gap="medium")

# --- Top știri ---
with col_news:
    hn = load_hn()
    if hn:
        for i, item in enumerate(hn[:3]):
            with st.container(border=True):
                st.markdown(
                    f'<div class="reveal reveal-{i+1}" style="color: var(--coral); '
                    f'font-family: JetBrains Mono, monospace; font-size: 0.7rem; '
                    f'letter-spacing: 0.06em; text-transform: uppercase; margin-bottom: 0.5rem;">'
                    f'📡 Știre #{i+1}</div>',
                    unsafe_allow_html=True,
                )
                st.markdown(f"**[{item.title[:90]}]({item.url})**")
                summary = (item.summary or "")[:140]
                if summary:
                    st.caption(summary + ("..." if len(item.summary or "") > 140 else ""))
                st.caption(f"HackerNews · ⬆ {item.score} · {fmt_date(item.published_at)}")

# --- Top unelte ---
with col_tools:
    repos = load_repos()
    if repos:
        for i, r in enumerate(repos[:3]):
            with st.container(border=True):
                st.markdown(
                    f'<div class="reveal reveal-{i+1}" style="color: var(--sky); '
                    f'font-family: JetBrains Mono, monospace; font-size: 0.7rem; '
                    f'letter-spacing: 0.06em; text-transform: uppercase; margin-bottom: 0.5rem;">'
                    f'⭐ Unealtă #{i+1}</div>',
                    unsafe_allow_html=True,
                )
                st.markdown(f"**[{r.full_name}]({r.url})**")
                desc = (r.description or "")[:120]
                if desc:
                    st.caption(desc + ("..." if len(r.description or "") > 120 else ""))
                st.caption(f"findarepo · ★ {r.stars} · ↗ +{r.growth}/7d · `{r.language}`")

# --- Top joburi ---
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
                f'font-family: JetBrains Mono, monospace; font-size: 0.7rem; '
                f'letter-spacing: 0.06em; text-transform: uppercase; margin-bottom: 0.5rem;">'
                f'💼 Job #{i+1}</div>',
                unsafe_allow_html=True,
            )
            st.markdown(f"**{j['title']}**")
            st.caption(f"{j['company']} · 📍 {j['location']}")
            st.markdown(
                f'<div style="font-family: Newsreader, serif; font-size: 1.6rem; '
                f'color: var(--sage); margin-top: 0.3rem;">{j["match"]}</div>',
                unsafe_allow_html=True,
            )
            st.caption("match score")
    st.caption("🚧 Live job feed vine în v0.6")

# --- Lesson + Prompt row ---
st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)

col_lesson, col_prompt = st.columns(2, gap="medium")

with col_lesson:
    st.markdown(
        '<p style="font-family: JetBrains Mono, monospace; font-size: 0.72rem; '
        'color: var(--sage); letter-spacing: 0.06em; text-transform: uppercase; '
        'margin: 0 0 1rem;">📚 Lecția zilei</p>',
        unsafe_allow_html=True,
    )
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
    st.markdown(
        '<p style="font-family: JetBrains Mono, monospace; font-size: 0.72rem; '
        'color: var(--lavender); letter-spacing: 0.06em; text-transform: uppercase; '
        'margin: 0 0 1rem;">🛠 Prompt de încercat</p>',
        unsafe_allow_html=True,
    )
    with st.container(border=True):
        st.markdown("### Explică-mi asta ca și cum aș avea 12 ani")
        st.caption(
            "Forțează LLM-ul să simplifice orice concept tehnic. "
            "Excelent pentru validarea înțelegerii tale."
        )
        st.markdown(
            '<pre style="background: var(--surface-2); padding: 0.8rem; '
            'border-radius: 8px; margin: 0.8rem 0; font-family: JetBrains Mono, '
            'monospace; font-size: 0.8rem; color: var(--text-2); white-space: pre-wrap;">'
            'Explică [concept] ca și cum aș avea 12 ani. '
            'Folosește o analogie din viața de zi cu zi.</pre>',
            unsafe_allow_html=True,
        )
        st.caption("🚧 Prompt Bible completă vine cu folder-ul tău")


# =====================================================================
# SECTION 2: STIRI — full feeds, organized by category
# =====================================================================
section_header(
    "📡",
    "Știri",
    "Deep dive pe 6 surse. Cercetare, comunitate, trenduri, analiză.",
    "coral",
)

# --- Research ---
st.markdown(
    '<p style="font-family: JetBrains Mono, monospace; font-size: 0.72rem; '
    'color: var(--sky); letter-spacing: 0.06em; text-transform: uppercase; '
    'margin: 0 0 1rem;">🔬 Cercetare · HuggingFace Papers</p>',
    unsafe_allow_html=True,
)
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

st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

# --- Community ---
st.markdown(
    '<p style="font-family: JetBrains Mono, monospace; font-size: 0.72rem; '
    'color: var(--coral); letter-spacing: 0.06em; text-transform: uppercase; '
    'margin: 0 0 1rem;">💬 Comunitate</p>',
    unsafe_allow_html=True,
)
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

st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

# --- Repos ---
st.markdown(
    '<p style="font-family: JetBrains Mono, monospace; font-size: 0.72rem; '
    'color: var(--lavender); letter-spacing: 0.06em; text-transform: uppercase; '
    'margin: 0 0 1rem;">⭐ Trenduri · GitHub</p>',
    unsafe_allow_html=True,
)
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

st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

# --- Analysis ---
st.markdown(
    '<p style="font-family: JetBrains Mono, monospace; font-size: 0.72rem; '
    'color: var(--coral); letter-spacing: 0.06em; text-transform: uppercase; '
    'margin: 0 0 1rem;">📰 Analiză săptămânală</p>',
    unsafe_allow_html=True,
)
ai_items = summarize_batch(load_importai()[:3])
if ai_items:
    for it in ai_items:
        with st.container(border=True):
            st.markdown(f"[{it.title}]({it.url})")
            st.markdown(f"_{it.summary}_")
            st.caption(f"📝 {it.author} · {fmt_date(it.published_at)}")


# =====================================================================
# SECTION 3: INVATA — AI Road course
# =====================================================================
section_header(
    "📚",
    "Învață",
    "Cursul complet. De la zero la product-ready AI.",
    "sage",
)

with st.container(border=True):
    st.markdown("### The AI Road")
    st.markdown(
        "Un ghid practic care te duce de la zero la product-ready. "
        "Fiecare capitol leagă teoria de ce se întâmplă azi în știri. "
        "În v0.4, fiecare capitol va fi queryabil prin RAG — "
        "pui o întrebare, primești context + legătură directă la capitol."
    )
    st.markdown(
        '<a href="../ai-beginners-guide/index.html" target="_blank">'
        '→ Deschide cursul complet</a>',
        unsafe_allow_html=True,
    )

st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
st.markdown("#### Cuprins")
st.caption("Cele 15 capitole ale cursului.")

chapters = [
    ("1", "Ce este AI-ul astăzi", "MIT, hype, realitate"),
    ("2", "Machine learning în 10 minute", "Supervised, unsupervised, reinforcement"),
    ("3", "Ce este un LLM", "Transformers, tokenizare, atenție"),
    ("4", "Cum antrenezi un model", "Pre-training, fine-tuning, RLHF"),
    ("5", "RAG — retrieval augmented generation", "Cum adaugi cunoștințe externe LLM-ului"),
    ("6", "Fine-tuning și adapters", "LoRA, QLoRA, PEFT"),
    ("7", "Agenți și tool use", "Când LLM-ul încetează să fie doar chatbot"),
    ("8", "Evaluare și metrici", "Cum știi dacă modelul tău e bun"),
    ("9", "Producție și cost", "Inference, latency, token economics"),
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
# SECTION 4: APLICĂ — Prompt Bible
# =====================================================================
section_header(
    "🛠",
    "Aplică",
    "Prompturi gata de folosit. Copiază, lipește, rezolvă.",
    "lavender",
)

with st.container(border=True):
    st.markdown("### Prompt Bible")
    st.markdown(
        '<p style="color: var(--lavender); font-family: JetBrains Mono, monospace; '
        'font-size: 0.72rem; letter-spacing: 0.06em; text-transform: uppercase; '
        'margin: 0.5rem 0 1rem;">🚧 În construcție</p>',
        unsafe_allow_html=True,
    )
    st.markdown(
        "Mii de prompturi organizate pe categorii — coding, writing, research, "
        "brainstorming, debugging, documentare. Cu search, tags, și exemplu de "
        "output pentru fiecare."
    )
    st.markdown(
        '<p style="color: var(--muted); margin-top: 1rem; font-style: italic;">'
        "Când folder-ul cu prompturi e gata, le integrăm aici. "
        "Până atunci, fă-ți cafeaua și folosește AZI pentru a vedea ce e nou."
        "</p>",
        unsafe_allow_html=True,
    )

st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
st.markdown("#### Starter pack")
st.caption("Câteva prompturi de bază ca să vezi vibe-ul.")

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
st.markdown("<div style='height: 4rem;'></div>", unsafe_allow_html=True)
st.markdown(
    '<div style="border-top: 1px solid var(--border); padding-top: 1.5rem; '
    'font-family: JetBrains Mono, monospace; font-size: 0.7rem; '
    'color: var(--muted-2); text-align: center; letter-spacing: 0.04em;">'
    'Ziarul Digital · v1.1 · pentru ingineri care beau cafeaua cu ochii pe lume'
    '</div>',
    unsafe_allow_html=True,
)