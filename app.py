"""Streamlit UI for Ziarul Digital · v1.0 redesign.

Four tabs, Headspace-inspired infusion palette:
  1. ☀️ ASTĂZI   — morning glance: top 3 from each category, 30 sec
  2. 📡 ȘTIRI   — deep dive on 6 sources
  3. 📚 ÎNVAȚĂ  — AI Road course (v0.4 placeholder for RAG)
  4. 🛠 APLICĂ  — Prompt Bible (placeholder for the folder)

Design tokens live in theme.py. Each tab gets its own accent color via
nth-child CSS rules — coral for news, sage for learning/jobs, lavender
for prompts.

Run: streamlit run app.py
"""
import streamlit as st
from datetime import datetime
from zoneinfo import ZoneInfo
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
from theme import render_css, COLORS, TAB_ACCENT


# ===== Page config =====
st.set_page_config(
    page_title="Ziarul Digital",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ===== Theme CSS =====
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
    """Render an ISO timestamp as '2h ago' / 'yesterday' / '3d ago'."""
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


# ===== Header =====
def render_header():
    """Top hero block. Calm, editorial, with date greeting."""
    col1, col2 = st.columns([5, 1])
    with col1:
        st.markdown(
            '<h1 style="margin-bottom: 0.25rem;">Ziarul Digital</h1>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<p style="font-family: Newsreader, serif; font-style: italic; color: var(--muted); margin-top: 0;">'
            'Every morning, your AI briefing in 60 seconds.'
            '</p>',
            unsafe_allow_html=True,
        )
    with col2:
        now = datetime.now(ZoneInfo("Europe/Bucharest"))
        date_label = now.strftime("%A · %d %B").lower()
        st.markdown(
            f'<div style="text-align: right; font-family: JetBrains Mono, monospace; '
            f'font-size: 0.75rem; color: var(--muted); letter-spacing: 0.04em;">'
            f'☀️ {date_label}'
            f'</div>',
            unsafe_allow_html=True,
        )
        if config.has_llm():
            st.markdown(
                '<div style="text-align: right; font-family: JetBrains Mono, monospace; '
                'font-size: 0.7rem; color: var(--sage); margin-top: 4px;">'
                '<span class="pulse-dot"></span>Groq connected</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div style="text-align: right; font-family: JetBrains Mono, monospace; '
                'font-size: 0.7rem; color: var(--muted-2); margin-top: 4px;">'
                '⚠ demo mode</div>',
                unsafe_allow_html=True,
            )


render_header()
st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)


# ===== Tabs =====
tab_astazi, tab_stiri, tab_invata, tab_aplica = st.tabs([
    "☀️ ASTĂZI",
    "📡 ȘTIRI",
    "📚 ÎNVAȚĂ",
    "🛠 APLICĂ",
])


# =====================================================================
# TAB 1: ASTĂZI — morning glance, 30 sec
# =====================================================================
with tab_astazi:
    st.markdown(
        '<p style="font-family: Newsreader, serif; font-style: italic; color: var(--muted); '
        'margin-top: -0.5rem; margin-bottom: 2rem;">'
        'Cele mai importante 3 din fiecare. Bea-ți cafeaua, scanează lumea.'
        '</p>',
        unsafe_allow_html=True,
    )

    # ---- 3 columns: News / Tools / Jobs ----
    col_news, col_tools, col_jobs = st.columns(3, gap="medium")

    # === Top News (coral) ===
    with col_news:
        st.markdown(
            '<h4 style="color: var(--coral); font-family: JetBrains Mono, monospace; '
            'font-size: 0.75rem; letter-spacing: 0.08em; text-transform: uppercase; '
            'margin-bottom: 1rem;"><span class="pulse-dot"></span>Top știri</h4>',
            unsafe_allow_html=True,
        )
        hn = load_hn()
        if hn:
            top_news = hn[:3]
            for i, item in enumerate(top_news):
                with st.container(border=True):
                    st.markdown(
                        f'<div class="reveal reveal-{i+1}">',
                        unsafe_allow_html=True,
                    )
                    st.markdown(f'**[{item.title[:80]}]({item.url})**')
                    summary = (item.summary or "")[:160]
                    if summary:
                        st.caption(summary + ("..." if len(item.summary) > 160 else ""))
                    st.caption(f"⬆ {item.score} · {fmt_date(item.published_at)}")
                    st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.caption("Nu s-au putut încărca știri.")

    # === Top Tools (sky) ===
    with col_tools:
        st.markdown(
            '<h4 style="color: var(--sky); font-family: JetBrains Mono, monospace; '
            'font-size: 0.75rem; letter-spacing: 0.08em; text-transform: uppercase; '
            'margin-bottom: 1rem;">⭐ Top unelte</h4>',
            unsafe_allow_html=True,
        )
        repos = load_repos()
        if repos:
            top_repos = repos[:3]
            for i, r in enumerate(top_repos):
                with st.container(border=True):
                    st.markdown(
                        f'<div class="reveal reveal-{i+1}">',
                        unsafe_allow_html=True,
                    )
                    st.markdown(f"**[{r.full_name}]({r.url})**")
                    desc = (r.description or "")[:120]
                    if desc:
                        st.caption(desc + ("..." if len(r.description) > 120 else ""))
                    st.caption(f"★ {r.stars} · ↗ +{r.growth}/7d · `{r.language}`")
                    st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.caption("Nu s-au putut încărca unelte.")

    # === Top Jobs (sage, mock for now) ===
    with col_jobs:
        st.markdown(
            '<h4 style="color: var(--sage); font-family: JetBrains Mono, monospace; '
            'font-size: 0.75rem; letter-spacing: 0.08em; text-transform: uppercase; '
            'margin-bottom: 1rem;">💼 Top joburi</h4>',
            unsafe_allow_html=True,
        )
        mock_jobs = [
            {"title": "LLM Engineer", "company": "DRUID AI", "location": "Bucharest", "match": "82%"},
            {"title": "AI Product Manager", "company": "Bitdefender", "location": "Bucharest", "match": "76%"},
            {"title": "AI Solutions Consultant", "company": "ClusterPower", "location": "Iași", "match": "71%"},
        ]
        for i, j in enumerate(mock_jobs):
            with st.container(border=True):
                st.markdown(
                    f'<div class="reveal reveal-{i+1}">',
                    unsafe_allow_html=True,
                )
                st.markdown(f"**{j['title']}**")
                st.caption(f"{j['company']} · 📍 {j['location']}")
                st.markdown(
                    f'<div style="font-family: Newsreader, serif; font-size: 1.5rem; '
                    f'color: var(--sage); margin-top: 0.3rem;">{j["match"]}</div>',
                    unsafe_allow_html=True,
                )
                st.caption("match score")
                st.markdown('</div>', unsafe_allow_html=True)
        st.caption("🚧 Live job feed vine în v0.6")

    # ---- Divider ----
    st.markdown(
        '<div style="height: 1px; background: var(--border); margin: 2.5rem 0 1.5rem;"></div>',
        unsafe_allow_html=True,
    )

    # ---- Bottom row: Today's lesson + Today's prompt ----
    col_lesson, col_prompt = st.columns(2, gap="medium")

    with col_lesson:
        st.markdown(
            '<h4 style="color: var(--sage); font-family: JetBrains Mono, monospace; '
            'font-size: 0.75rem; letter-spacing: 0.08em; text-transform: uppercase; '
            'margin-bottom: 1rem;">📚 Lecția zilei</h4>',
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
            '<h4 style="color: var(--lavender); font-family: JetBrains Mono, monospace; '
            'font-size: 0.75rem; letter-spacing: 0.08em; text-transform: uppercase; '
            'margin-bottom: 1rem;">🛠 Prompt de încercat</h4>',
            unsafe_allow_html=True,
        )
        with st.container(border=True):
            st.markdown("### Explică-mi asta ca și cum aș avea 12 ani")
            st.caption(
                '<span style="color: var(--muted);">Forțează LLM-ul să simplifice '
                "orice concept tehnic. Excelent pentru validarea înțelegerii tale.</span>",
                unsafe_allow_html=True,
            )
            st.markdown(
                '<pre style="background: var(--surface-2); padding: 0.8rem; '
                'border-radius: 8px; margin: 0.8rem 0; font-family: JetBrains Mono, '
                'monospace; font-size: 0.8rem; color: var(--text-2); white-space: '
                'pre-wrap;">Explică [concept] ca și cum aș avea 12 ani. '
                'Folosește o analogie din viața de zi cu zi.</pre>',
                unsafe_allow_html=True,
            )
            st.caption("🚧 Prompt Bible completă vine cu folder-ul tău")


# =====================================================================
# TAB 2: ȘTIRI — deep dive on 6 sources
# =====================================================================
with tab_stiri:

    st.markdown(
        '<p style="font-family: Newsreader, serif; font-style: italic; color: var(--muted); '
        'margin-top: -0.5rem; margin-bottom: 2rem;">'
        'Toate știrile din toate sursele. Romaneste, cu context.'
        '</p>',
        unsafe_allow_html=True,
    )

    # ---- Today's Research (HF Papers) ----
    st.markdown("#### 🔬 Today's Research")
    st.caption("Top papers trending on HuggingFace · sky")

    papers = summarize_batch(load_hf()[:5])
    if papers:
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
                        st.button("🔍", key=f"paper-{p.external_id}", use_container_width=True)
                    else:
                        st.button("🔒", key=f"paper-lock-{p.external_id}", disabled=True, use_container_width=True)

    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

    # ---- Community Buzz (HN + Lobsters) ----
    st.markdown("#### 💬 Community Buzz")
    st.caption("Discussions from HackerNews · coral and Lobsters · sage")

    col_hn, col_lob = st.columns(2, gap="medium")

    with col_hn:
        st.markdown(
            '<div style="color: var(--coral); font-family: JetBrains Mono, monospace; '
            'font-size: 0.75rem; letter-spacing: 0.06em; text-transform: uppercase; '
            'margin-bottom: 0.5rem;">🔥 HackerNews</div>',
            unsafe_allow_html=True,
        )
        hn_items = summarize_batch(load_hn()[:6])
        if hn_items:
            for item in hn_items:
                with st.container(border=True):
                    st.markdown(f"[{item.title}]({item.url})")
                    st.caption(f"⬆ {item.score} · 👤 {item.author or 'anon'} · {fmt_date(item.published_at)}")
        else:
            st.caption("Nu s-au putut încărca știri HN.")

    with col_lob:
        st.markdown(
            '<div style="color: var(--sage); font-family: JetBrains Mono, monospace; '
            'font-size: 0.75rem; letter-spacing: 0.06em; text-transform: uppercase; '
            'margin-bottom: 0.5rem;">🦞 Lobsters</div>',
            unsafe_allow_html=True,
        )
        lob_items = summarize_batch(load_lobsters()[:6])
        if lob_items:
            for item in lob_items:
                with st.container(border=True):
                    st.markdown(f"[{item.title}]({item.url})")
                    st.caption(f"⬆ {item.score} · 👤 {item.author or 'anon'} · {fmt_date(item.published_at)}")
        else:
            st.caption("Nu s-au putut încărca povești Lobsters.")

    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

    # ---- Trending Repos ----
    st.markdown("#### ⭐ Trending Repos")
    st.caption("findarepo · lavender and GitHub Trending · sky")

    col_fr, col_gh = st.columns(2, gap="medium")

    with col_fr:
        st.markdown(
            '<div style="color: var(--lavender); font-family: JetBrains Mono, monospace; '
            'font-size: 0.75rem; letter-spacing: 0.06em; text-transform: uppercase; '
            'margin-bottom: 0.5rem;">📊 findarepo · 7-day growth</div>',
            unsafe_allow_html=True,
        )
        repos = load_repos()[:6]
        if repos:
            for r in repos:
                with st.container(border=True):
                    st.markdown(f"[{r.full_name}]({r.url})")
                    st.caption(f"★ {r.stars} total · ↗ +{r.growth}/7d · `{r.language}`")
        else:
            st.caption("Nu s-au putut încărca repo-uri findarepo.")

    with col_gh:
        st.markdown(
            '<div style="color: var(--sky); font-family: JetBrains Mono, monospace; '
            'font-size: 0.75rem; letter-spacing: 0.06em; text-transform: uppercase; '
            'margin-bottom: 0.5rem;">🔥 GitHub Trending · today</div>',
            unsafe_allow_html=True,
        )
        gh_items = load_github()[:6]
        if gh_items:
            for it in gh_items:
                with st.container(border=True):
                    st.markdown(f"[{it.title}]({it.url})")
                    tags_short = "/".join(t for t in it.tags if t not in ("github", "repo", "trending")) or "—"
                    st.caption(f"⬆ {it.score} stars today · `{tags_short}`")
        else:
            st.caption("Nu s-au putut încărca repo-uri GitHub.")

    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

    # ---- Weekly Analysis ----
    st.markdown("#### 📰 Deep Analysis")
    st.caption("Weekly essays from Jack Clark's Import AI · coral")

    ai_items = summarize_batch(load_importai()[:3])
    if ai_items:
        for it in ai_items:
            with st.container(border=True):
                cols = st.columns([6, 1])
                with cols[0]:
                    st.markdown(f"##### [{it.title}]({it.url})")
                    st.markdown(f"_{it.summary}_")
                    st.caption(f"📝 {it.author} · {fmt_date(it.published_at)}")
                with cols[1]:
                    st.button("📖", key=f"ai-{it.external_id}", use_container_width=True)


# =====================================================================
# TAB 3: ÎNVAȚĂ — AI Road course (v0.4 placeholder for RAG)
# =====================================================================
with tab_invata:

    st.markdown(
        '<p style="font-family: Newsreader, serif; font-style: italic; color: var(--muted); '
        'margin-top: -0.5rem; margin-bottom: 2rem;">'
        'Învață ce e în spatele știrilor. Cursul complet, în română.'
        '</p>',
        unsafe_allow_html=True,
    )

    # Hero card
    with st.container(border=True):
        st.markdown("### The AI Road")
        st.caption("Curs complet, 15 capitole · pentru ingineri care vor să înțeleagă AI-ul dincolo de buzzwords")
        st.markdown(
            "Un ghid practic care te duce de la zero la product-ready. "
            "Fiecare capitol leagă teoria de ce se întâmplă azi în știri."
        )
        st.markdown(
            '<a href="../ai-beginners-guide/index.html" target="_blank">'
            '→ Deschide cursul complet</a>',
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)

    # Chapter preview
    st.markdown("#### Cuprins")
    st.caption("În v0.4, fiecare capitol va fi queryabil prin RAG — pune o întrebare, primești context + legătură.")

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
            cols = st.columns([1, 5])
            with cols[0]:
                st.markdown(
                    f'<div style="font-family: Newsreader, serif; font-size: 2rem; '
                    f'color: var(--sage); line-height: 1;">{num}</div>',
                    unsafe_allow_html=True,
                )
            with cols[1]:
                st.markdown(f"**{title}**")
                st.caption(blurb)


# =====================================================================
# TAB 4: APLICĂ — Prompt Bible (placeholder)
# =====================================================================
with tab_aplica:

    st.markdown(
        '<p style="font-family: Newsreader, serif; font-style: italic; color: var(--muted); '
        'margin-top: -0.5rem; margin-bottom: 2rem;">'
        'Prompturi gata de folosit. Copiază, lipește, rezolvă.'
        '</p>',
        unsafe_allow_html=True,
    )

    # Coming-soon hero
    with st.container(border=True):
        st.markdown("### Prompt Bible")
        st.markdown(
            '<p style="color: var(--lavender); font-family: JetBrains Mono, monospace; '
            'font-size: 0.75rem; letter-spacing: 0.08em; text-transform: uppercase; '
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
            "Până atunci, fă-ți cafeaua și folosește ASTĂZI pentru a vedea ce e nou."
            "</p>",
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)

    # Mini preview — a few starter prompts so the tab isn't empty
    st.markdown("#### Starter pack (până vine Prompt Bible completă)")
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
                f'<span style="color: var(--lavender); font-family: JetBrains Mono, monospace; '
                f'font-size: 0.7rem;">{p["category"].upper()}</span>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<pre style="background: var(--surface-2); padding: 0.7rem; '
                f'border-radius: 6px; margin: 0.6rem 0 0; font-family: JetBrains Mono, '
                f'monospace; font-size: 0.78rem; color: var(--text-2); white-space: '
                f'pre-wrap;">{p["prompt"]}</pre>',
                unsafe_allow_html=True,
            )


# ===== Footer =====
st.markdown("<div style='height: 3rem;'></div>", unsafe_allow_html=True)
st.markdown(
    '<div style="border-top: 1px solid var(--border); padding-top: 1.5rem; '
    'font-family: JetBrains Mono, monospace; font-size: 0.7rem; '
    'color: var(--muted-2); text-align: center; letter-spacing: 0.04em;">'
    'Ziarul Digital · v1.0 · pentru ingineri care beau cafeaua cu ochii pe lume'
    '</div>',
    unsafe_allow_html=True,
)