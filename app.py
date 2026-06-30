"""OpenRadar · Streamlit UI v3.

Layout:
  ┌──────────────┬─────────────────────────────────────┐
  │  sidebar     │  section content (max 1080px)       │
  │   • brand    │                                     │
  │   • nav      │                                     │
  │   • status   │                                     │
  └──────────────┴─────────────────────────────────────┘

Each of the 5 sections (groq / news / learning / jobs / prompts) is
rendered by its own `render_*` function. The sidebar calls `render_*`
based on the radio selection. Helpers (card, hero, bento, nav) live at
the top and are reused everywhere.

Run: streamlit run app.py
"""
from __future__ import annotations

import html
import json
import random
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional
from zoneinfo import ZoneInfo

import streamlit as st


def _columns(spec, gap="small", vertical_alignment="center"):
    """Backwards-compatible `st.columns` wrapper.

    Streamlit 1.50+ supports `vertical_alignment`; 1.32 (HF Spaces)
    doesn't. Drop the kwarg on older versions.
    """
    import inspect
    if "vertical_alignment" in inspect.signature(st.columns).parameters:
        return st.columns(spec, gap=gap, vertical_alignment=vertical_alignment)
    return st.columns(spec, gap=gap)

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
from learning import (
    get_chapter,
    get_all_chapters,
    DOMAIN_META,
    domain_color,
)
from learning.insight import ask_groq
from learning import progress as _progress  # PR1: ?p=... persistence transport
import config
from theme import render_css, COLORS, SECTION_ACCENT
from tips import TIPS as ALL_TIPS
from prompts import (
    load_prompt_bible,
    category_label,
    category_icon,
    category_color,
    difficulty_label,
    difficulty_color,
    all_categories,
    all_difficulties,
    all_model_ids,
)


# ─── PR1 persistence: restore from ?p=... before any Learning state reads ───
# Streamlit has already populated session_state with widget keys by the time
# the page body runs, but the only "default" key we touch here is "section".
# We restore Learning progress BEFORE render_top_nav runs so that any
# subsequent read of selected_chapter / completed_chapters sees the restored
# values. Never raises. Never strips the param.
_progress.apply_incoming_query_param(st.session_state, st.query_params)  # type: ignore[arg-type]  # Streamlit's SessionStateProxy is structurally SessionStateLike; Pyright is over-strict at the integration boundary.


# ─── Page setup ─────────────────────────────────────────────────────────
st.set_page_config(
    page_title="OpenRadar",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="collapsed",  # sidebar is dead — top nav now
)
st.markdown(render_css(), unsafe_allow_html=True)

# Ambient overlays — radar rings (top-right) + slow scan line
st.markdown(
    '<div class="or-radar" aria-hidden="true"></div>'
    '<div class="or-scan" aria-hidden="true"></div>',
    unsafe_allow_html=True,
)


# ─── Inline SVG icons ───────────────────────────────────────────────────
# Lucide-style stroke icons. Shapes only — class is supplied at the call
# site so a single icon can render at multiple sizes/colors.

ICON_SHAPES = {
    "sun":      ('<circle cx="12" cy="12" r="4"/>'
                 '<path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41'
                 'M17.66 17.66l1.41 1.41M2 12h2M20 12h2'
                 'M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41"/>'),
    "antenna":  ('<path d="M2 12c2-3 5-5 10-5s8 2 10 5"/>'
                 '<path d="M5 15c1-2 4-3.5 7-3.5s6 1.5 7 3.5"/>'
                 '<path d="M8.5 18c.5-1 1.7-1.7 3.5-1.7s3 .7 3.5 1.7"/>'
                 '<circle cx="12" cy="20" r="1.2" fill="currentColor"/>'),
    "book":     ('<path d="M4 4h7a3 3 0 0 1 3 3v13a2 2 0 0 0-2-2H4z"/>'
                 '<path d="M20 4h-7a3 3 0 0 0-3 3v13a2 2 0 0 1 2-2h8z"/>'),
    "briefcase":('<rect x="3" y="7" width="18" height="13" rx="2"/>'
                 '<path d="M8 7V5a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>'
                 '<path d="M3 13h18"/>'),
    "spark":    ('<path d="M12 3l2 5 5 2-5 2-2 5-2-5-5-2 5-2z"/>'
                 '<path d="M19 14l.7 1.7L21 16l-1.3.3L19 18l-.7-1.7'
                 'L17 16l1.3-.3z"/>'),
    "bento":    ('<rect x="3" y="3" width="8" height="8" rx="1"/>'
                 '<rect x="13" y="3" width="8" height="5" rx="1"/>'
                 '<rect x="13" y="10" width="8" height="11" rx="1"/>'
                 '<rect x="3" y="13" width="8" height="8" rx="1"/>'),
    "compass":  ('<circle cx="12" cy="12" r="9"/>'
                 '<path d="M15 9l-2 6-6 2 2-6z"/>'),
    "case":     ('<rect x="3" y="7" width="18" height="13" rx="2"/>'
                 '<path d="M8 7V5a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>'),
}


def icon(name: str, cls: str = "nav-ico") -> str:
    """Render an inline SVG icon by name. String concat (avoids f-string
    backslash issues on Python 3.9)."""
    return (
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" '
        'class="' + cls + '">' + ICON_SHAPES[name] + '</svg>'
    )


# Brand radar mark — concentric rings with four spokes. Explicit
# width/height so the SVG can't fall back to browser-default 300x150px
# when the surrounding CSS hasn't been applied yet.
RADAR_MARK = (
    '<svg width="22" height="22" viewBox="0 0 32 32" fill="none" '
    'stroke="currentColor" stroke-width="1.2" stroke-linecap="round" '
    'class="or-mark">'
    '<circle cx="16" cy="16" r="13"/>'
    '<circle cx="16" cy="16" r="8" opacity="0.6"/>'
    '<circle cx="16" cy="16" r="3" opacity="0.85"/>'
    '<line x1="16" y1="2" x2="16" y2="6" opacity="0.7"/>'
    '<line x1="16" y1="26" x2="16" y2="30" opacity="0.7"/>'
    '<line x1="2" y1="16" x2="6" y2="16" opacity="0.7"/>'
    '<line x1="26" y1="16" x2="30" y2="16" opacity="0.7"/>'
    '</svg>'
)


# ─── Data loaders (cached) ──────────────────────────────────────────────
@st.cache_data(ttl=1800, show_spinner=False)
def load_hn():       return fetch_hackernews_ai(limit=8) or []

@st.cache_data(ttl=3600, show_spinner=False)
def load_hf():       return fetch_hf_papers(limit=8) or []

@st.cache_data(ttl=3600, show_spinner=False)
def load_repos():    return fetch_findarepo_daily(limit=8) or []

@st.cache_data(ttl=3600, show_spinner=False)
def load_github():   return fetch_github_trending(limit=8) or []

@st.cache_data(ttl=1800, show_spinner=False)
def load_lobsters(): return fetch_lobsters(limit=8) or []

@st.cache_data(ttl=86400, show_spinner=False)
def load_importai(): return fetch_importai(limit=5) or []


# ─── Helpers ────────────────────────────────────────────────────────────
def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def fmt_date(iso_str: str) -> str:
    if not iso_str:
        return ""
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        now = datetime.now(ZoneInfo("UTC"))
        delta = now - dt
        if delta.days == 0:
            h = delta.seconds // 3600
            if h == 0:
                m = max(delta.seconds // 60, 1)
                return f"{m}m ago"
            return f"{h}h ago"
        if delta.days == 1:
            return "yesterday"
        if delta.days < 7:
            return f"{delta.days}d ago"
        return dt.strftime("%b %d")
    except (ValueError, AttributeError):
        return iso_str[:10] or ""


def live_badge(text: str = "LIVE FEED") -> str:
    """Pulsing green pill — used in hero eyebrow & top bar."""
    return (
        '<span class="or-live"><span class="dot"></span>'
        f'{esc(text)}</span>'
    )


def section_head(eyebrow: str, title: str, caption: str = "") -> None:
    """Standard top-of-section header. Used on News / Jobs / Prompts."""
    cap = f'<p class="or-caption">{esc(caption)}</p>' if caption else ""
    st.markdown(
        f'<div class="or-section-head or-reveal">'
        f'<span class="or-eyebrow">{esc(eyebrow)}</span>'
        f'<div><h1>{esc(title)}</h1></div>'
        f'{cap}'
        f'</div>',
        unsafe_allow_html=True,
    )


def hero_block(eyebrow_html: str, headline_html: str, sub: str) -> None:
    """Cinematic centered hero for the Groq landing.

    `eyebrow_html` is trusted HTML (caller built it). `sub` is plain
    text and gets escaped here.
    """
    st.markdown(
        '<div class="or-hero or-reveal">'
        f'<div class="or-eyebrow">{eyebrow_html}</div>'
        f'<h1>{headline_html}</h1>'
        f'<p class="or-sub">{esc(sub)}</p>'
        '</div>',
        unsafe_allow_html=True,
    )


def top_bar(caption: str = "") -> None:
    """Single-row top bar: live pill on left, italic caption on right."""
    live = live_badge("LIVE FEED")
    cap_html = f'<span class="or-caption">{esc(caption)}</span>' if caption else ""
    st.markdown(
        '<div class="or-top-bar or-reveal">'
        f'<div>{live}</div>'
        f'<div>{cap_html}</div>'
        '</div>',
        unsafe_allow_html=True,
    )


def or_card(
    label: str,
    label_color: str,
    title: str,
    title_url: Optional[str] = None,
    summary: str = "",
    meta: str = "",
    meta_html: Optional[str] = None,
    summary_limit: int = 140,
) -> None:
    """One news / repo / lesson card. Single hairline border, soft hover."""
    if title_url:
        title_block = (
            f'<a class="or-card-link" href="{esc(title_url)}" target="_blank">'
            f'<span class="or-card-title">{esc(title)}</span></a>'
        )
    else:
        title_block = f'<span class="or-card-title">{esc(title)}</span>'

    if summary:
        s_trim = summary[:summary_limit]
        suffix = "…" if len(summary) > summary_limit else ""
        sum_block = f'<p class="or-card-summary">{esc(s_trim)}{suffix}</p>'
    else:
        sum_block = ""

    if meta_html is not None:
        meta_block = f'<div class="or-card-meta">{meta_html}</div>'
    elif meta:
        meta_block = f'<div class="or-card-meta">{esc(meta)}</div>'
    else:
        meta_block = ""

    st.markdown(
        f'<div class="or-card">'
        f'<div class="or-card-label {esc(label_color)}">{esc(label)}</div>'
        f'{title_block}'
        f'{sum_block}'
        f'{meta_block}'
        f'</div>',
        unsafe_allow_html=True,
    )


def bento_card(icon_key: str, title: str, count: int, accent: str, body_html: str) -> str:
    """One cell of a bento grid — returns HTML, caller wraps with `.or-bento`."""
    return (
        '<div class="or-bento-card">'
        '<div class="or-bento-head">'
        + icon(icon_key, "or-bento-icon")
        + f'<span class="or-bento-title" style="color:{accent};">{esc(title)}</span>'
        + f'<span class="or-bento-count">{count}</span>'
        '</div>'
        + body_html +
        '</div>'
    )


def bento_open(inner_html: str) -> str:
    return f'<div class="or-bento">{inner_html}</div>'


# ─── Tips cycling strip (ambient wisdom) ───────────────────────────────
def _build_tip_lines(n: int = 4, seed_key: str = "tips_v3") -> str:
    if seed_key not in st.session_state:
        rng = random.Random()
        rng.seed()
        st.session_state[seed_key] = rng.sample(ALL_TIPS, min(n, len(ALL_TIPS)))

    rows = []
    for cat, body, _attrib in st.session_state[seed_key]:
        body_esc = body.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        rows.append(
            '<div class="or-tip-line">'
            f'<span class="or-tip-cat tip-cat {esc(cat)}">{esc(cat)}</span>'
            f'<span class="or-tip-body">{body_esc}</span>'
            '</div>'
        )
    return "".join(rows)


def tips_strip(n: int = 4) -> None:
    """Full-width cycling dev-tip pill — only on Groq landing."""
    st.markdown(
        '<div class="or-tips or-reveal">'
        '<span class="or-tips-tag">TIP</span>'
        '<div class="or-tips-slot">'
        + _build_tip_lines(n=n) +
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )


# ─── Top nav (sidebar is dead) ─────────────────────────────────────────
def render_top_nav() -> str:
    """Render the top nav row. Returns the active section id.

    Desktop:  ┌──────────┬─────────────────────────┬──────────────┐
              │ brand    │ 5-pill button group     │ status + act │
              └──────────┴─────────────────────────┴──────────────┘

    Mobile (≤720px, CSS-only): stack into 3 rows — brand on top, full-
    width pills below, status + refresh at the bottom. CSS handles it
    via .or-topnav and `.or-nav-pills` rules in theme.py.
    """
    if "section" not in st.session_state:
        # Allow `?section=learning` deep-link via query params
        _qp = st.query_params.get("section", "groq")
        _valid = {"groq", "news", "learning", "jobs", "prompts"}
        st.session_state.section = _qp if _qp in _valid else "groq"

    cols = _columns([1.4, 4.2, 1.6], gap="medium")

    # Brand
    with cols[0]:
        st.markdown(
            '<a class="or-topnav-brand" href="?section=groq">'
            f'{RADAR_MARK}'
            '<span class="or-name">OpenRadar</span>'
            '</a>',
            unsafe_allow_html=True,
        )

    # 5 nav buttons — each renders as a Streamlit `st.button` in its
    # own column. CSS handles the pill styling via [class*="st-key-nav_"].
    with cols[1]:
        section_labels = [
            ("groq",     "☀  Groq"),
            ("news",     "◌  News"),
            ("learning", "❡  Learning"),
            ("jobs",     "◆  Jobs"),
            ("prompts",  "✦  Prompts"),
        ]
        st.markdown('<div class="or-nav-pills">', unsafe_allow_html=True)
        btn_cols = st.columns(5, gap="small")
        for (key, label), col in zip(section_labels, btn_cols):
            with col:
                if st.button(
                    label,
                    key=f"nav_{key}",
                    use_container_width=True,
                    type="primary" if st.session_state.section == key else "secondary",
                ):
                    st.session_state.section = key
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # Status + refresh action
    with cols[2]:
        is_live = config.has_llm()
        dot_cls = "" if is_live else "demo"
        status_text = "ONLINE" if is_live else "DEMO"

        inner = _columns([3, 1.2], gap="small")
        with inner[0]:
            st.markdown(
                f'<div class="or-topnav-status">'
                f'<span class="or-live-pill">'
                f'<span class="or-status-dot {dot_cls}"></span>'
                f'<span>{status_text}</span>'
                f'</span>'
                f'<span class="or-tag-desktop" style="opacity:.5;">· v3</span>'
                f'</div>',
                unsafe_allow_html=True,
            )
        with inner[1]:
            if st.button("↻", key="nav_refresh", use_container_width=True,
                         help="Refresh feeds (clear cache)"):
                st.cache_data.clear()
                st.toast("Cache cleared.")
                st.rerun()

    return st.session_state.section


SECTION = render_top_nav()

# Fallback for unknown / stale section values
if SECTION not in {"groq", "news", "learning", "jobs", "prompts"}:
    SECTION = "groq"
    st.session_state.section = "groq"


# ─────────────────────────────────────────────────────────────────────────
# SECTION: AZI · daily brief landing
# ─────────────────────────────────────────────────────────────────────────
def render_groq() -> None:
    """The default landing: cinematic hero, then a 3-card bento of
    News / Tools / Jobs (top 3 each), then a mini-bento for lesson + prompt."""

    hero_block(
        eyebrow_html=(
            "<span class='or-live'>"
            "<span class='dot'></span>LIVE · BUCUREȘTI · "
            + datetime.now(ZoneInfo("Europe/Bucharest")).strftime("%a %d %b").upper()
            + "</span>"
        ),
        headline_html=(
            'Today, in <span class="or-accent">signals</span>.'
        ),
        sub="Bei cafeaua, scanezi lumea, pleci la treaba. "
            "Top 3 din fiecare · lecția zilei · un prompt de încercat.",
    )

    tips_strip(n=4)

    # ── Bento: News / Tools / Jobs (one cell each) ──
    hn = load_hn()[:3]

    # Always normalize repos to a common dict shape, regardless of source.
    # findarepo returns TrendingRepo dataclass; github_trending returns NewsItem.
    repo_dicts = [
        {
            "full_name":  r.full_name,
            "description": r.description,
            "url":        r.url,
            "stars":      r.stars,
            "growth":     f"+{r.growth}/7d" if r.growth and not str(r.growth).startswith("+") else str(r.growth),
            "language":   r.language or "—",
            "source":     "findarepo",
        }
        for r in load_repos()[:3]
    ]
    if not repo_dicts:
        repo_dicts = [
            {
                "full_name":  it.title,
                "description": it.summary or "",
                "url":        it.url,
                "stars":      str(it.score),
                "growth":     "today",
                "language":   (it.tags[0] if it.tags else "—"),
                "source":     "GitHub",
            }
            for it in load_github()[:3]
        ]

    mock_jobs = [
        {"title": "LLM Engineer", "company": "DRUID AI", "location": "București", "match": "82%"},
        {"title": "AI Product Manager", "company": "Bitdefender", "location": "București", "match": "76%"},
        {"title": "AI Solutions Consultant", "company": "ClusterPower", "location": "Iași", "match": "71%"},
    ]

    news_body = "".join(
        f'<div class="or-card" style="margin-bottom:.5rem;background:transparent;border-color:var(--border);">'
        f'<div class="or-card-label coral">▸ HN FEED</div>'
        f'<a class="or-card-link" href="{esc(item.url)}" target="_blank">'
        f'<span class="or-card-title">{esc(item.title[:70])}</span></a>'
        f'<p class="or-card-summary">{esc(item.summary[:100])}</p>'
        f'<div class="or-card-meta">⬆ {item.score} · {esc(fmt_date(item.published_at))}</div>'
        f'</div>'
        for item in hn
    ) or '<div style="color:var(--muted);font-style:italic;font-size:.85rem;">Curăță cache-ul și încearcă din nou.</div>'

    tools_body = "".join(
        '<div class="or-card" style="margin-bottom:.5rem;background:transparent;border-color:var(--border);">'
        f'<div class="or-card-label sky">▸ {esc(rd.get("source","").upper())} · {esc(str(rd.get("language","")).upper())}</div>'
        f'<a class="or-card-link" href="{esc(rd.get("url","#"))}" target="_blank">'
        f'<span class="or-card-title">{esc(rd.get("full_name", rd.get("title",""))[:70])}</span></a>'
        f'<p class="or-card-summary">{esc(rd.get("description", rd.get("summary",""))[:100])}</p>'
        f'<div class="or-card-meta">★ {esc(str(rd.get("stars","")))} · ↗ {esc(str(rd.get("growth","+")))}</div>'
        '</div>'
        for rd in repo_dicts
    ) or '<div style="color:var(--muted);font-style:italic;font-size:.85rem;">findarepo offline. Încearcă GitHub Trending.</div>'

    jobs_body = "".join(
        f'<div class="or-card" style="margin-bottom:.5rem;background:transparent;border-color:var(--border);">'
        f'<div class="or-card-label sage">▸ {esc(j["location"].upper())}</div>'
        f'<span class="or-card-title">{esc(j["title"])}</span>'
        f'<p class="or-card-summary" style="margin-bottom:.35rem;">{esc(j["company"])}</p>'
        f'<div class="or-card-meta"><span class="or-card-score" style="font-size:1rem;">{esc(j["match"])}</span>'
        f'<span style="text-transform:uppercase;">match</span></div>'
        f'</div>'
        for j in mock_jobs
    )

    bento_html = (
        bento_open(
            bento_card("bento",   "News",  len(hn),          COLORS["coral"],  news_body) +
            bento_card("compass", "Tools", len(repo_dicts),  COLORS["sky"],    tools_body) +
            bento_card("case",    "Jobs",  len(mock_jobs),   COLORS["sage"],   jobs_body)
        )
    )
    st.markdown(bento_html, unsafe_allow_html=True)

    # ── Mini-bento: lesson + prompt ──
    st.markdown(
        '<div class="or-bento-mini or-reveal-2">'
        '<div class="or-mini">'
        '<div class="or-mini-tag">▸ LESSON TODAY</div>'
        '<h3>Ce este un LLM?</h3>'
        '<p class="or-mini-body">Rețele neuronale antrenate pe cantități '
        'masive de text. Învață pattern-uri statistice care le permit să '
        'genereze text coerent, să răspundă la întrebări și să raționeze '
        'într-o oarecare măsură.</p>'
        '<div class="or-mini-foot">'
        '<span>Capitolul 3 · 5 min</span>'
        '<a href="../ai-beginners-guide/index.html#chapter-3" target="_blank">Citește capitolul →</a>'
        '</div>'
        '</div>'
        '<div class="or-mini prompts">'
        '<div class="or-mini-tag">▸ PROMPT TO TRY</div>'
        '<h3>Explică-mi ca și cum aș avea 12 ani</h3>'
        '<p class="or-mini-body">Forțează LLM-ul să simplifice orice concept '
        'tehnic, înainte să-l aplici. Cel mai bun test dacă chiar ai înțeles '
        'ceva.</p>'
        '<div class="or-mini-foot">'
        '<span>beginner · any model</span>'
        '<a href="?section=prompts">Vezi prompturi →</a>'
        '</div>'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    # Footer line — minimal
    st.markdown(
        '<div style="margin-top:4rem;padding-top:1.5rem;border-top:1px solid var(--border);'
        'font-family:JetBrains Mono,monospace;font-size:.65rem;color:var(--muted-2);'
        'text-align:center;letter-spacing:.04em;">'
        'OpenRadar · pentru ingineri care beau cafeaua cu ochii pe lume'
        '</div>',
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────────────────────────────────
# SECTION: NEWS · full feed from 6 sources
# ─────────────────────────────────────────────────────────────────────────
def render_news() -> None:
    section_head(
        "FEED · ȘASE SURSE",
        "News",
        "Deep dive pe 6 surse: cercetare, comunitate, trenduri, analiză.",
    )

    # 1. Research (HF papers)
    st.markdown(
        '<p style="font-family:JetBrains Mono,monospace;font-size:.7rem;'
        'letter-spacing:.18em;text-transform:uppercase;color:var(--sky);'
        'margin:0 0 1rem;">▸ Cercetare</p>',
        unsafe_allow_html=True,
    )
    for p in summarize_batch(load_hf()[:5]):
        or_card(
            label="HF Papers",
            label_color="sky",
            title=p.title,
            title_url=p.url,
            summary=p.summary,
            meta=f"⬆ {p.score} · 👤 {esc(p.author or 'anon')}",
        )

    # 2. Community — HN + Lobsters side-by-side
    st.markdown('<div style="height:1.8rem;"></div>', unsafe_allow_html=True)
    st.markdown(
        '<p style="font-family:JetBrains Mono,monospace;font-size:.7rem;'
        'letter-spacing:.18em;text-transform:uppercase;color:var(--coral);'
        'margin:0 0 1rem;">▸ Comunitate</p>',
        unsafe_allow_html=True,
    )
    col_hn, col_lob = st.columns(2, gap="medium")
    with col_hn:
        st.caption("HackerNews")
        for item in summarize_batch(load_hn()[:5]):
            or_card(
                label="HN",
                label_color="coral",
                title=item.title,
                title_url=item.url,
                summary=item.summary,
                meta=f"⬆ {item.score} · {fmt_date(item.published_at)}",
            )
    with col_lob:
        st.caption("Lobsters")
        for item in summarize_batch(load_lobsters()[:5]):
            or_card(
                label="Lobsters",
                label_color="coral",
                title=item.title,
                title_url=item.url,
                summary=item.summary,
                meta=f"⬆ {item.score} · {fmt_date(item.published_at)}",
            )

    # 3. Trends
    st.markdown('<div style="height:1.8rem;"></div>', unsafe_allow_html=True)
    st.markdown(
        '<p style="font-family:JetBrains Mono,monospace;font-size:.7rem;'
        'letter-spacing:.18em;text-transform:uppercase;color:var(--lavender);'
        'margin:0 0 1rem;">▸ Trenduri GitHub</p>',
        unsafe_allow_html=True,
    )
    col_fr, col_gh = st.columns(2, gap="medium")
    with col_fr:
        st.caption("findarepo · 7-day growth")
        for r in load_repos()[:5]:
            or_card(
                label="findarepo",
                label_color="sky",
                title=r.full_name,
                title_url=r.url,
                summary=r.description,
                meta=f"★ {r.stars} · ↗ +{r.growth}/7d · {esc(r.language or '—')}",
            )
    with col_gh:
        st.caption("GitHub Trending · today")
        for it in load_github()[:5]:
            tags = "/".join(t for t in it.tags if t not in ("github", "repo", "trending")) or "—"
            or_card(
                label="GitHub",
                label_color="sky",
                title=it.title,
                title_url=it.url,
                meta=f"⬆ {it.score} stars · {esc(tags)}",
            )

    # 4. Weekly analysis
    st.markdown('<div style="height:1.8rem;"></div>', unsafe_allow_html=True)
    st.markdown(
        '<p style="font-family:JetBrains Mono,monospace;font-size:.7rem;'
        'letter-spacing:.18em;text-transform:uppercase;color:var(--coral);'
        'margin:0 0 1rem;">▸ Analiză săptămânală</p>',
        unsafe_allow_html=True,
    )
    for it in summarize_batch(load_importai()[:3]):
        or_card(
            label="Import AI",
            label_color="lavender",
            title=it.title,
            title_url=it.url,
            summary=it.summary,
            meta=f"📝 {esc(it.author or '')} · {fmt_date(it.published_at)}",
        )


# ─────────────────────────────────────────────────────────────────────────
# SECTION: LEARNING · Hartă AI pe categorii (10 chapters)
# ─────────────────────────────────────────────────────────────────────────
def render_learning() -> None:
    from learning.timeline import render_hero_timeline
    from learning.learning_render import render_detail_panel

    section_head(
        "HARTĂ AI · 10 CATEGORII",
        "Learning",
        "Fiecare capitol = o categorie mare de AI. Basics + un exercițiu.",
    )

    st.markdown(
        '<p style="font-family:Newsreader,serif;font-style:italic;color:#c4b9a7;'
        'font-size:1.05rem;margin:0 0 1.4rem;line-height:1.55;max-width:680px;">'
        'LLMs, prompting, vision, diffusion, speech, RAG, agenți. '
        '10 capitole, fiecare cu un «Build this» pe care îl faci ACUM. '
        'Nu citi totul — fă primul exercițiu și treci la următorul.'
        '</p>',
        unsafe_allow_html=True,
    )

    st.markdown(render_hero_timeline(), unsafe_allow_html=True)

    # ── Chapter chip grid ──
    selected_id = st.session_state.get("selected_chapter", "ch1")
    ch_list = get_all_chapters()

    st.markdown(
        '<p style="margin:1.5rem 0 .7rem;font-family:JetBrains Mono,monospace;'
        'font-size:.65rem;color:var(--muted);letter-spacing:.18em;'
        'text-transform:uppercase;">'
        'Capitole · 10 categorii AI, fiecare cu un «Build this»</p>',
        unsafe_allow_html=True,
    )

    chip_cols_per_row = 5
    for row_start in range(0, len(ch_list), chip_cols_per_row):
        row = ch_list[row_start:row_start + chip_cols_per_row]
        c_cols = st.columns(len(row), gap="small")
        for ci, c in enumerate(row):
            with c_cols[ci]:
                # Single styled button per chip. The button itself IS the chip;
                # primary/secondary type carries the selected vs muted state.
                # The accent color for the selected state is supplied via a
                # small inline `<style>` per chapter using testid attributes
                # in 1.50+ fall back to plain pill style below.
                title = c.title if len(c.title) <= 18 else c.title[:16].rstrip() + "…"
                if st.button(
                    f"{c.number:02d}  {title}",
                    key=f"lrn_chip_{c.id}",
                    use_container_width=True,
                    type="primary" if c.id == selected_id else "secondary",
                ):
                    st.session_state.selected_chapter = c.id
                    st.rerun()

    # ── Detail panel ──
    completed = st.session_state.get("completed_chapters", set())
    render_detail_panel(selected_id, ch_list, completed)


# ─────────────────────────────────────────────────────────────────────────
# SECTION: JOBS · mock data + future
# ─────────────────────────────────────────────────────────────────────────
def render_jobs() -> None:
    section_head(
        "MATCH · SKILL GAPS",
        "Jobs",
        "Joburi AI care se potrivesc cu ce înveți. Skill matching LLM-powered.",
    )

    mock_jobs = [
        {"title": "LLM Engineer", "company": "DRUID AI", "location": "București", "match": "82%", "gap": "LangChain, Vector DBs"},
        {"title": "AI Product Manager", "company": "Bitdefender", "location": "București", "match": "76%", "gap": "Eval, RAG"},
        {"title": "AI Solutions Consultant", "company": "ClusterPower", "location": "Iași", "match": "71%", "gap": "GPU infrastructure"},
        {"title": "ML Engineer", "company": "UiPath", "location": "București", "match": "68%", "gap": "Fine-tuning, RLHF"},
    ]

    # 2-up bento of mock jobs
    cards_html = ""
    for j in mock_jobs:
        cards_html += (
            '<div class="or-mini" style="min-height:auto;">'
            f'<div class="or-mini-tag">▸ {esc(j["location"].upper())}</div>'
            f'<h3 style="font-size:1.15rem;margin-bottom:.35rem;">{esc(j["title"])}</h3>'
            f'<p class="or-mini-body" style="margin-bottom:.8rem;">{esc(j["company"])} '
            f'· <span style="color:var(--muted);">skills gap: {esc(j["gap"])}</span></p>'
            f'<div class="or-mini-foot"><span style="font-family:Newsreader,serif;'
            f'font-size:1.4rem;color:var(--amber);font-style:italic;">{esc(j["match"])}</span>'
            f'<span>match</span></div></div>'
        )
    st.markdown(
        f'<div class="or-bento-mini or-reveal" '
        f'style="grid-template-columns:repeat(2,1fr);">{cards_html}</div>',
        unsafe_allow_html=True,
    )

    # Future notice
    st.markdown('<div style="height:2rem;"></div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="or-mini or-reveal" style="min-height:auto;">'
        '<div class="or-mini-tag" style="color:var(--coral);">▸ ROADMAP · V0.6</div>'
        '<h3>Live job feed — în construcție</h3>'
        '<p class="or-mini-body">Scrape LinkedIn, Indeed, BestJobs și eJobs. '
        'Extrage skill-uri cu LLM. Match-ează cu profilul tău. Sugerează '
        'capitole din Learning pentru skill gaps.</p>'
        '</div>',
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────────────────────────────────
# SECTION: PROMPTS · Prompt Bible
# ─────────────────────────────────────────────────────────────────────────
def render_prompts() -> None:
    bible = load_prompt_bible()
    n_total = len(bible.prompts)
    cats   = all_categories(bible)
    diffs  = all_difficulties()
    models = all_model_ids(bible)

    # Pre-compute category counts for the pill labels
    cat_counts = {c["id"]: 0 for c in bible.categories}
    for p in bible.prompts:
        c = p.get("category", "")
        if c in cat_counts:
            cat_counts[c] += 1

    section_head(
        f"PROMPT BIBLE · {n_total}",
        "Prompts",
        "Prompturi production-grade. Filtrează pe categorie, "
        "difficulty sau model — caută în titlu și conținut.",
    )

    # ── Search ──
    text_q = st.text_input(
        "Caută",
        placeholder="Caută în titlu, tag-uri, conținut...",
        label_visibility="collapsed",
        key="prompts_search",
    )

    # ── Category pills ──
    st.markdown(
        '<p style="margin:1rem 0 .4rem;font-family:JetBrains Mono,monospace;'
        'font-size:.65rem;letter-spacing:.18em;text-transform:uppercase;color:var(--muted);">'
        'Categorie</p>',
        unsafe_allow_html=True,
    )
    selected_cats = list(st.session_state.get("prompts_cats", []))
    cat_per_row = 4
    for r0 in range(0, len(cats), cat_per_row):
        row = cats[r0:r0 + cat_per_row]
        cols = st.columns(len(row), gap="small")
        for i, c in enumerate(row):
            with cols[i]:
                is_sel = c in selected_cats
                label = f"{category_icon(bible, c)} {category_label(bible, c)} · {cat_counts[c]}"
                if st.button(label, key=f"pill_cat_{c}", use_container_width=True,
                             type="primary" if is_sel else "secondary"):
                    if is_sel:
                        selected_cats.remove(c)
                    else:
                        selected_cats.append(c)
                    st.session_state["prompts_cats"] = selected_cats
                    st.rerun()

    # ── Difficulty pills ──
    st.markdown(
        '<p style="margin:.8rem 0 .4rem;font-family:JetBrains Mono,monospace;'
        'font-size:.65rem;letter-spacing:.18em;text-transform:uppercase;color:var(--muted);">'
        'Difficulty</p>',
        unsafe_allow_html=True,
    )
    selected_diffs = list(st.session_state.get("prompts_diffs", []))
    d_cols = st.columns(len(diffs), gap="small")
    for i, d in enumerate(diffs):
        with d_cols[i]:
            is_sel = d in selected_diffs
            if st.button(difficulty_label(d), key=f"pill_diff_{d}",
                         use_container_width=True,
                         type="primary" if is_sel else "secondary"):
                if is_sel:
                    selected_diffs.remove(d)
                else:
                    selected_diffs.append(d)
                st.session_state["prompts_diffs"] = selected_diffs
                st.rerun()

    # ── Model pills ──
    st.markdown(
        '<p style="margin:.8rem 0 .4rem;font-family:JetBrains Mono,monospace;'
        'font-size:.65rem;letter-spacing:.18em;text-transform:uppercase;color:var(--muted);">'
        'Modele</p>',
        unsafe_allow_html=True,
    )
    selected_models = list(st.session_state.get("prompts_models", []))
    per_row = 8
    for r0 in range(0, len(models), per_row):
        row = models[r0:r0 + per_row]
        cols = st.columns(len(row), gap="small")
        for i, m in enumerate(row):
            with cols[i]:
                is_sel = m in selected_models
                if st.button(bible.models.get(m, {}).get("label", m),
                             key=f"pill_model_{m}", use_container_width=True,
                             type="primary" if is_sel else "secondary"):
                    if is_sel:
                        selected_models.remove(m)
                    else:
                        selected_models.append(m)
                    st.session_state["prompts_models"] = selected_models
                    st.rerun()

    # ── Sort + reset ──
    sort_cols = st.columns([3, 1], gap="small")
    with sort_cols[0]:
        sort_label = st.radio(
            "Sortare",
            options=["Default", "A→Z", "Beginner → Expert", "Expert → Beginner"],
            horizontal=True,
            label_visibility="collapsed",
            key="prompts_sort",
        )
    with sort_cols[1]:
        any_active = bool(text_q or selected_cats or selected_diffs or selected_models)
        if any_active and st.button("✕  Resetează", key="prompts_reset",
                                     use_container_width=True):
            st.session_state["prompts_search"] = ""
            st.session_state["prompts_cats"] = []
            st.session_state["prompts_diffs"] = []
            st.session_state["prompts_models"] = []
            st.session_state["prompts_sort"] = "Default"
            st.rerun()

    # ── Filter ──
    results = []
    needle = text_q.strip().lower()
    for p in bible.prompts:
        if selected_cats   and p.get("category")   not in selected_cats:    continue
        if selected_diffs  and p.get("difficulty") not in selected_diffs:   continue
        if selected_models and not any(m in p.get("models", []) for m in selected_models): continue
        if needle:
            hay = " ".join([
                p.get("title", ""),
                " ".join(p.get("tags", []) or []),
                p.get("when", ""),
                p.get("prompt", ""),
                " ".join(p.get("notes", []) or []),
            ]).lower()
            if needle not in hay: continue
        results.append(p)

    if sort_label == "A→Z":
        results.sort(key=lambda p: p.get("title", "").lower())
    elif sort_label == "Beginner → Expert":
        results.sort(key=lambda p: diffs.index(p.get("difficulty", "intermediate")))
    elif sort_label == "Expert → Beginner":
        results.sort(key=lambda p: -diffs.index(p.get("difficulty", "intermediate")))

    n = len(results)
    any_filter = bool(text_q or selected_cats or selected_diffs or selected_models)
    st.markdown(
        f'<div style="display:flex;align-items:baseline;gap:.6rem;margin:1.4rem 0 .6rem;'
        f'font-family:Newsreader,serif;">'
        f'<span style="font-size:1.8rem;color:var(--text);font-weight:500;">{n}</span>'
        f'<span style="font-family:JetBrains Mono,monospace;font-size:.7rem;color:var(--muted);'
        f'text-transform:uppercase;letter-spacing:.08em;">'
        f'/ {n_total} prompturi'
        f'{" · filtrat" if any_filter else ""}</span></div>',
        unsafe_allow_html=True,
    )

    # ── Results ──
    if n == 0:
        st.markdown(
            '<div style="padding:2rem;text-align:center;color:var(--muted);'
            'font-style:italic;border:1px dashed var(--border);border-radius:8px;margin:1rem 0;">'
            'Nimic pe filtre. Schimbă text sau categorie.'
            '</div>',
            unsafe_allow_html=True,
        )
        return

    for p in results:
        cat_id = p.get("category", "")
        cat_lbl = category_label(bible, cat_id)
        cat_clr = category_color(bible, cat_id)
        diff    = p.get("difficulty", "intermediate")
        diff_clr= difficulty_color(diff)

        title = p.get("title", "Untitled")
        when  = p.get("when", "")
        tags  = p.get("tags", []) or []
        pmods = p.get("models", []) or []
        body  = p.get("prompt", "")
        variants = p.get("variants") or {}
        notes    = p.get("notes") or []
        anti     = p.get("antiPatterns") or []

        tags_html = "".join(f'<span class="or-card-meta" style="margin-right:.35rem;">{esc(t)}</span>' for t in tags[:6])
        models_html = " · ".join(bible.models.get(m, {}).get("label", m) for m in pmods)
        when_block = f'<p style="font-family:Newsreader,serif;font-style:italic;color:var(--muted);margin:.4rem 0;font-size:.95rem;">{esc(when)}</p>' if when else ""

        st.markdown(
            '<div style="padding:.6rem 0 1.1rem;border-bottom:1px solid var(--border);margin-bottom:.4rem;">'
            '<div style="display:flex;align-items:center;gap:.6rem;margin-bottom:.4rem;flex-wrap:wrap;">'
            f'<span style="font-family:Newsreader,serif;font-size:1.2rem;color:var(--text);'
            f'font-weight:500;flex:1;line-height:1.2;">{esc(title)}</span>'
            f'<span style="font-family:JetBrains Mono,monospace;font-size:.6rem;'
            f'letter-spacing:.08em;text-transform:uppercase;padding:.15rem .55rem;'
            f'border:1px solid {cat_clr}55;border-radius:999px;color:{cat_clr};">{esc(cat_lbl)}</span>'
            f'<span style="font-family:JetBrains Mono,monospace;font-size:.6rem;'
            f'letter-spacing:.08em;text-transform:uppercase;padding:.15rem .55rem;'
            f'border:1px solid {diff_clr}55;border-radius:999px;color:{diff_clr};">{esc(difficulty_label(diff))}</span>'
            '</div>'
            f'{when_block}'
            '<div style="display:flex;flex-wrap:wrap;gap:.3rem;margin-bottom:.4rem;">'
            f'{tags_html}'
            '</div>'
            f'<div style="font-family:JetBrains Mono,monospace;font-size:.62rem;color:var(--muted-2);">'
            f'{esc(models_html)}</div>'
            '</div>',
            unsafe_allow_html=True,
        )

        if variants:
            tab_labels = ["default"] + list(variants.keys())
            tabs = st.tabs(tab_labels)
            with tabs[0]:
                st.code(body, language="text")
            for i, (vname, vbody) in enumerate(variants.items(), start=1):
                with tabs[i]:
                    st.code(vbody, language="text")
        else:
            st.code(body, language="text")

        if notes or anti:
            with st.expander("De ce merge · Ce îl strică"):
                if notes:
                    st.markdown("**De ce merge**")
                    for n_line in notes:
                        st.markdown(f"- {esc(n_line)}")
                if anti:
                    st.markdown("**Ce îl strică**")
                    for a_line in anti:
                        st.markdown(f"- {esc(a_line)}")


# ─── Dispatch ───────────────────────────────────────────────────────────
DISPATCH = {
    "groq":     render_groq,
    "news":     render_news,
    "learning": render_learning,
    "jobs":     render_jobs,
    "prompts":  render_prompts,
}

# Fallback for unknown section values coming from the URL or stale state
SECTION = SECTION if SECTION in DISPATCH else "groq"

# Run the chosen renderer
DISPATCH[SECTION]()


# ─── PR1 persistence: write the latest snapshot back into ?p=... ──────────
# After DISPATCH[SECTION]() returns, Streamlit's widget replay has populated
# session_state with every verifier_* / method_done_* key for the current
# render. We snapshot the full state (chapters-driven for the Learning keys,
# plain for navigation) and write it to ?p=... only if it changed. The loop
# guard (``_progress_last_token`` in session_state) prevents the kind of
# assignment→rerun→assignment loop that would otherwise loop forever in
# Streamlit's reactive model.
try:
    _progress.sync_query_param(
        st.session_state,  # type: ignore[arg-type]  # see comment above
        st.query_params,
        chapters=get_all_chapters(),
    )
except Exception:
    # Sync is best-effort: never crash the page over a persistence write.
    pass
