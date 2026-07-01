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
    KITS,           # PR10 — outcome-grouped prompt bundles
    kits_for,       # PR10 — build the kit list from the loaded bible
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
    '<svg width="26" height="26" viewBox="0 0 32 32" fill="none" '
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

    # Brand — icon + name + small mono kicker for hierarchy.
    with cols[0]:
        st.markdown(
            '<a class="or-topnav-brand" href="?section=groq">'
            f'{RADAR_MARK}'
            '<span class="or-name-stack">'
            '<span class="or-name">OpenRadar</span>'
            '<span class="or-name-kicker">ai career · tools radar</span>'
            '</span>'
            '</a>',
            unsafe_allow_html=True,
        )

    # 5 nav buttons — each renders as a Streamlit `st.button` in its
    # own column. CSS handles the pill styling via [class*="st-key-nav_"].
    # Display labels are user-facing; internal section keys stay the
    # same so `?section=groq` deep-links and the DISPATCH dict keep
    # working without rename risk.
    #
    # PR10 positioning labels: Today / Tools / Learn / Jobs / Prompt Kits.
    # NOTE — internal key `news` is temporarily retained for the Tools tab
    # to avoid a risky deep-link rename. Tracked as follow-up debt.
    with cols[1]:
        section_labels = [
            ("groq",     "☀  Today"),
            ("news",     "◌  Tools"),
            ("learning", "❡  Learn"),
            ("jobs",     "◆  Jobs"),
            ("prompts",  "✦  Prompt Kits"),
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
# SECTION: AZI · today landing
# PR10 positioning: "Today" — daily brief for an AI Career + Tools Radar.
# Bento trio is News / Tools / Jobs (top 3 each) + lesson + prompt.
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
            'Your <span class="or-accent">AI career</span> &amp; tools radar.'
        ),
        sub="O dată pe zi, cinci semnale: ce e nou azi, un tool pe care să-l încerci, "
            "o lecție scurtă și un kit de prompturi pentru mâine.",
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

    # PR10 patch: Today landing — static role teaser, no fake match%.
    # Mirrors the Jobs tab framing (role · company · location · skill tags)
    # but kept compact for the bento cell. Title is the link to the Jobs tab.
    static_roles = [
        {"title": "LLM Engineer",            "company": "DRUID AI",        "location": "București", "skill": "LangChain · Vector DBs"},
        {"title": "AI Product Manager",      "company": "Bitdefender",     "location": "București", "skill": "Eval · RAG"},
        {"title": "AI Solutions Consultant", "company": "ClusterPower",    "location": "Iași",      "skill": "GPU · Fine-tuning"},
        {"title": "ML Engineer",             "company": "UiPath",          "location": "București", "skill": "Fine-tuning · RLHF"},
    ][:3]  # bento cell = top 3 only

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
        f'<p class="or-card-summary" style="margin-bottom:.35rem;">{esc(j["company"])} · '
        f'<span style="font-family:JetBrains Mono,monospace;font-size:.55rem;color:var(--muted);">'
        f'{esc(j["skill"])}</span></p>'
        f'<div class="or-card-meta"><a href="?section=jobs" style="font-family:JetBrains Mono,monospace;'
        f'font-size:.6rem;letter-spacing:.08em;text-transform:uppercase;color:var(--sage);">'
        f'Search paths →</a></div>'
        f'</div>'
        for j in static_roles
    )

    bento_html = (
        bento_open(
            bento_card("bento",   "Today Signals", len(hn),          COLORS["coral"],  news_body) +
            bento_card("compass", "Tools",         len(repo_dicts),  COLORS["sky"],    tools_body) +
            bento_card("case",    "Jobs",          len(static_roles), COLORS["sage"],  jobs_body)
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
# SECTION: TOOLS · curated by use case (internal key still `news`)
# PR10: Tools replaces the old News feed. Reorganized into 4 outcome-
# keyed buckets (Build / Ship / Write-Decide / Discover), each capped
# at 4 cards. Function name `render_news` retained to avoid touching
# DISPATCH; the user-facing label in the top nav is now "Tools".
# See decision log for rationale.
# ─────────────────────────────────────────────────────────────────────────
def render_news() -> None:
    section_head(
        "CURATED · BY USE CASE",
        "Tools",
        "Patru grupări de lucru — Build / Ship / Write &amp; Decide / Discover. "
        "Patru carduri per grupare, nu un dump. Folosește ca să alegi un tool pentru "
        "ce vrei să faci azi.",
    )

    # 1. Build software — repos trending on 7-day growth + GitHub today
    st.markdown(
        '<p style="font-family:JetBrains Mono,monospace;font-size:.7rem;'
        'letter-spacing:.18em;text-transform:uppercase;color:var(--sky);'
        'margin:1.5rem 0 .8rem;">▸ Build software</p>'
        '<p style="font-family:Newsreader,serif;font-style:italic;color:var(--muted);'
        'font-size:.9rem;margin:-.4rem 0 1rem;">Repos trending on growth. '
        'Pick one to read, fork, or integrate.</p>',
        unsafe_allow_html=True,
    )
    repos = list(load_repos()[:2]) + list(load_github()[:2])
    if not repos:
        st.markdown(
            '<div style="color:var(--muted);font-style:italic;font-size:.85rem;">'
            'Feed offline. Încearcă din nou.</div>',
            unsafe_allow_html=True,
        )
    for r in repos:
        if hasattr(r, "full_name"):  # TrendingRepo dataclass from findarepo
            or_card(
                label="findarepo · build",
                label_color="sky",
                title=r.full_name,
                title_url=r.url,
                summary=r.description,
                meta=f"★ {r.stars} · ↗ +{r.growth}/7d · {esc(r.language or '—')}",
            )
        else:  # NewsItem from github_trending
            tags = "/".join(t for t in r.tags if t not in ("github", "repo", "trending")) or "—"
            or_card(
                label="GitHub · build",
                label_color="sky",
                title=r.title,
                title_url=r.url,
                meta=f"⬆ {r.score} stars · {esc(tags)}",
            )

    # 2. Ship faster — research + community signal on what's deployable now
    st.markdown(
        '<p style="font-family:JetBrains Mono,monospace;font-size:.7rem;'
        'letter-spacing:.18em;text-transform:uppercase;color:var(--lavender);'
        'margin:1.5rem 0 .8rem;">▸ Ship faster</p>'
        '<p style="font-family:Newsreader,serif;font-style:italic;color:var(--muted);'
        'font-size:.9rem;margin:-.4rem 0 1rem;">Research + community signal — '
        'what is deployable today vs what is still in the lab.</p>',
        unsafe_allow_html=True,
    )
    for p in summarize_batch(load_hf()[:2] + load_hn()[:2]):
        or_card(
            label=f"{'HF Papers' if p.url and 'arxiv' in p.url else 'HN'} · ship",
            label_color="lavender" if "arxiv" in (p.url or "") else "coral",
            title=p.title,
            title_url=p.url,
            summary=p.summary,
            meta=f"⬆ {p.score} · {fmt_date(p.published_at)}",
        )

    # 3. Write &amp; decide — opinion + analysis
    st.markdown(
        '<p style="font-family:JetBrains Mono,monospace;font-size:.7rem;'
        'letter-spacing:.18em;text-transform:uppercase;color:var(--coral);'
        'margin:1.5rem 0 .8rem;">▸ Write &amp; decide</p>'
        '<p style="font-family:Newsreader,serif;font-style:italic;color:var(--muted);'
        'font-size:.9rem;margin:-.4rem 0 1rem;">Opinion + analysis — long-form '
        'pieces that change how you frame a decision.</p>',
        unsafe_allow_html=True,
    )
    combined = list(load_lobsters()[:2]) + list(load_importai()[:2])
    if not combined:
        st.markdown(
            '<div style="color:var(--muted);font-style:italic;font-size:.85rem;">'
            'Opinion feed offline. Încearcă din nou.</div>',
            unsafe_allow_html=True,
        )
    for it in summarize_batch(combined):
        or_card(
            label="Lobsters" if "lobste.rs" in (it.url or "") else "Import AI",
            label_color="coral",
            title=it.title,
            title_url=it.url,
            summary=it.summary,
            meta=f"⬆ {it.score} · {fmt_date(it.published_at)}",
        )

    # 4. Discover this week — fresh + emerging
    st.markdown(
        '<p style="font-family:JetBrains Mono,monospace;font-size:.7rem;'
        'letter-spacing:.18em;text-transform:uppercase;color:var(--amber);'
        'margin:1.5rem 0 .8rem;">▸ Discover this week</p>'
        '<p style="font-family:Newsreader,serif;font-style:italic;color:var(--muted);'
        'font-size:.9rem;margin:-.4rem 0 1rem;">Fresh, weird, worth a 30-second '
        'skim — rising fast, niche today, possibly inevitable next quarter.</p>',
        unsafe_allow_html=True,
    )
    emerging = list(load_hn()[:2]) + list(load_lobsters()[:2])
    if not emerging:
        st.markdown(
            '<div style="color:var(--muted);font-style:italic;font-size:.85rem;">'
            'Discover feed offline.</div>',
            unsafe_allow_html=True,
        )
    for it in summarize_batch(emerging):
        or_card(
            label="Discover",
            label_color="amber",
            title=it.title,
            title_url=it.url,
            summary=it.summary,
            meta=f"⬆ {it.score} · {fmt_date(it.published_at)}",
        )


# ─────────────────────────────────────────────────────────────────────────
# SECTION: LEARN · Practical short paths (10 chapters)
# PR10: copy nudge — frames the 10 chapters as practical short paths,
# not a generic course catalog. Content itself is unchanged.
# ─────────────────────────────────────────────────────────────────────────
def render_learning() -> None:
    from learning.learning_render import render_detail_panel
    from theme import lecture_css

    section_head(
        "PATHS · 10 CHAPTERS",
        "Learn",
        "Zece capitole scurte, fiecare cu un exercițiu. Basics + o treabă concretă de "
        "făcut — nu curs generic.",
    )

    ch_list = get_all_chapters()
    # Defensive: if the loader somehow returned 0, fall back to a no-op panel.
    if not ch_list:
        return

    # ── Calm chapter selector (replaces the 5x2 chip grid) ──
    selected_id = st.session_state.get("selected_chapter", ch_list[0].id)
    # Guard against a stale id pointing at a retired or missing chapter.
    if selected_id not in {c.id for c in ch_list}:
        selected_id = ch_list[0].id
        st.session_state.selected_chapter = selected_id

    def _format_chapter(c) -> str:
        title = c.title if len(c.title) <= 48 else c.title[:46].rstrip() + "…"
        return f"{c.number:02d} · {title}"

    chosen = st.selectbox(
        "Capitol",
        options=ch_list,
        index=[c.id for c in ch_list].index(selected_id),
        format_func=_format_chapter,
        key="learning_chapter_selectbox",
        label_visibility="collapsed",
    )
    if chosen.id != selected_id:
        st.session_state.selected_chapter = chosen.id
        st.rerun()
    selected_id = chosen.id

    # ── Single-column lecture page ──
    completed = st.session_state.get("completed_chapters", set())
    st.markdown(lecture_css(), unsafe_allow_html=True)
    render_detail_panel(selected_id, ch_list, completed)


# ─────────────────────────────────────────────────────────────────────────
# SECTION: JOBS · static role + skill search-path map
# PR10: This is intentionally NOT a live job board. Each entry is a
# role + skill anchor with outbound search paths (LinkedIn / BestJobs /
# eJobs / Indeed RO) so the user can leave the app and actually search.
# Skill gaps point back into the Learn chapters. Live aggregation is a
# later milestone — see roadmap note at the bottom of this section.
# ─────────────────────────────────────────────────────────────────────────
def render_jobs() -> None:
    section_head(
        "ROLE MAP · SEARCH PATHS",
        "Jobs",
        "Patru roluri AI care angajează activ în RO. Pentru fiecare: abilități, "
        "capitol de învățat, și link-uri de căutare pe platformele care contează. "
        "Nu e job board — e hartă.",
    )

    st.markdown(
        '<div class="or-mini or-reveal" style="min-height:auto;margin:0 0 1.4rem;">'
        '<div class="or-mini-tag" style="color:var(--sky);">▸ HOW THIS WORKS</div>'
        '<p class="or-mini-body" style="margin-bottom:0;">'
        'Alege un rol · citește gap-ul · mergi la capitolul recomandat · aplică '
        'prin link-urile de search de mai jos. Board-ul live e pe roadmap; pentru '
        'acum, platformele reale sunt mai bune decât orice scraper.'
        '</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    # Role + skill + search-path cards. Static content.
    # Each role: title, company, location, skills_needed (tags),
    # related_chapter (from content/chapters.jsonl), search_paths
    # (outbound links to real job platforms).
    roles = [
        {
            "title": "LLM Engineer",
            "company": "DRUID AI",
            "location": "București",
            "skills": ["Python", "LangChain", "Vector DBs", "RAG"],
            "chapter_id": "ch5",   # building with LLMs
            "search": [
                ("LinkedIn", "https://www.linkedin.com/jobs/search/?keywords=LLM%20Engineer%20DRUID"),
                ("BestJobs", "https://www.bestjobs.eu/ro/locuri-de-munca?q=LLM%20Engineer"),
                ("eJobs",    "https://www.ejobs.ro/locuri-de-munca?q=LLM%20Engineer"),
                ("Indeed RO","https://ro.indeed.com/jobs?q=LLM+Engineer"),
            ],
        },
        {
            "title": "AI Product Manager",
            "company": "Bitdefender",
            "location": "București",
            "skills": ["Eval design", "RAG strategy", "Stakeholder demos"],
            "chapter_id": "ch7",   # product/apply chapter
            "search": [
                ("LinkedIn", "https://www.linkedin.com/jobs/search/?keywords=AI%20Product%20Manager%20Bitdefender"),
                ("BestJobs", "https://www.bestjobs.eu/ro/locuri-de-munca?q=AI%20Product%20Manager"),
                ("eJobs",    "https://www.ejobs.ro/locuri-de-munca?q=AI%20Product%20Manager"),
                ("Indeed RO","https://ro.indeed.com/jobs?q=AI+Product+Manager"),
            ],
        },
        {
            "title": "AI Solutions Consultant",
            "company": "ClusterPower",
            "location": "Iași",
            "skills": ["GPU infra", "Fine-tuning", "On-prem LLM"],
            "chapter_id": "ch6",   # infra / RAG chapter
            "search": [
                ("LinkedIn", "https://www.linkedin.com/jobs/search/?keywords=AI%20Solutions%20Consultant"),
                ("BestJobs", "https://www.bestjobs.eu/ro/locuri-de-munca?q=AI%20Consultant"),
                ("eJobs",    "https://www.ejobs.ro/locuri-de-munca?q=AI%20Consultant"),
                ("Indeed RO","https://ro.indeed.com/jobs?q=AI+Solutions"),
            ],
        },
        {
            "title": "ML Engineer",
            "company": "UiPath",
            "location": "București",
            "skills": ["Fine-tuning", "RLHF", "Eval pipelines"],
            "chapter_id": "ch8",   # applied/build chapter
            "search": [
                ("LinkedIn", "https://www.linkedin.com/jobs/search/?keywords=ML%20Engineer%20UiPath"),
                ("BestJobs", "https://www.bestjobs.eu/ro/locuri-de-munca?q=ML%20Engineer"),
                ("eJobs",    "https://www.ejobs.ro/locuri-de-munca?q=ML%20Engineer"),
                ("Indeed RO","https://ro.indeed.com/jobs?q=ML+Engineer"),
            ],
        },
    ]

    # 2-up bento of role cards
    cards_html = ""
    for r in roles:
        skills_html = "".join(
            f'<span style="font-family:JetBrains Mono,monospace;font-size:.6rem;'
            f'letter-spacing:.06em;text-transform:uppercase;padding:.15rem .5rem;'
            f'border:1px solid var(--border);border-radius:999px;color:var(--muted);'
            f'margin-right:.3rem;">{esc(s)}</span>'
            for s in r["skills"]
        )
        paths_html = "".join(
            f'<a href="{esc(url)}" target="_blank" rel="noopener" '
            f'style="font-family:JetBrains Mono,monospace;font-size:.62rem;'
            f'letter-spacing:.08em;text-transform:uppercase;color:var(--sky);'
            f'margin-right:.6rem;">{esc(name)} ↗</a>'
            for name, url in r["search"]
        )
        chapter_url = f"?section=learning&ch={r['chapter_id']}"
        cards_html += (
            '<div class="or-mini" style="min-height:auto;">'
            f'<div class="or-mini-tag">▸ {esc(r["location"].upper())} · {esc(r["company"].upper())}</div>'
            f'<h3 style="font-size:1.15rem;margin-bottom:.5rem;">{esc(r["title"])}</h3>'
            f'<div style="margin-bottom:.7rem;">{skills_html}</div>'
            f'<div class="or-mini-foot" style="flex-direction:column;align-items:flex-start;gap:.5rem;">'
            f'<div>{paths_html}</div>'
            f'<a href="{esc(chapter_url)}" style="font-family:Newsreader,serif;font-style:italic;'
            f'font-size:.85rem;color:var(--amber);">→ Capitolul pentru gap-ul ăsta</a>'
            f'</div>'
            f'</div>'
        )
    st.markdown(
        f'<div class="or-bento-mini or-reveal" '
        f'style="grid-template-columns:repeat(2,1fr);">{cards_html}</div>',
        unsafe_allow_html=True,
    )

    # Roadmap note — explicit, no fake live feed promise
    st.markdown('<div style="height:2rem;"></div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="or-mini or-reveal" style="min-height:auto;">'
        '<div class="or-mini-tag" style="color:var(--coral);">▸ ROADMAP</div>'
        '<h3>Live job feed — nu azi</h3>'
        '<p class="or-mini-body">'
        'Scraping live de pe LinkedIn / Indeed / BestJobs / eJobs este pe lista '
        'de <em>later</em>. Până atunci, folosește link-urile de search de mai '
        'sus — sunt reale, indexate, și au filtre pe care orice job board le '
        'poate doar copia. Când adăugăm live, facem explicit (badge-ul va '
        'spune «LIVE FEED» și va fi etichetat ca atare).'
        '</p>'
        '</div>',
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────────────────────────────────
# SECTION: PROMPT KITS · outcome-grouped bundles (primary layer)
# PR10: Prompt Kits is the primary product surface on this tab. Below
# the kits row, the full Prompt Bible (1,137 prompts + filters) is kept
# as a secondary power-user/search layer. Internal key still `prompts`.
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
        "KITS · BY OUTCOME",
        "Prompt Kits",
        "Cinci kit-uri pentru o treabă specifică — un kit pentru azi, restul "
        "când ai nevoie. Colecția completă (1.137 prompturi) e mai jos, cu filtre.",
    )

    # ── Primary layer: Kits (outcome-grouped prompt bundles) ──
    bundles = kits_for(bible)

    kit_cells = ""
    for i, kit in enumerate(bundles):
        cid = kit.get("category", "code")
        clr = category_color(bible, cid)
        lbl = category_label(bible, cid)
        ico = category_icon(bible, cid)
        sample = kit.get("prompts", [])[:5]
        sample_html = "".join(
            f'<a href="?section=prompts&amp;kit={esc(kit["id"])}" '
            f'style="font-family:Newsreader,serif;font-size:.92rem;color:var(--text);'
            f'line-height:1.35;display:block;margin-bottom:.35rem;text-decoration:none;">'
            f'<span style="color:{esc(clr)};">▸</span> {esc(p.get("title",""))}</a>'
            for p in sample
        )
        anchor = "?section=prompts&kit=" + kit["id"]
        more = max(0, len(kit.get("prompts", [])) - len(sample))
        more_html = (
            f'<a href="{esc(anchor)}" style="font-family:JetBrains Mono,monospace;'
            f'font-size:.62rem;letter-spacing:.08em;text-transform:uppercase;'
            f'color:var(--amber);">+ {more} more in this kit →</a>'
            if more else ""
        )
        kit_cells += (
            '<div class="or-mini" style="min-height:auto;">'
            f'<div class="or-mini-tag" style="color:{esc(clr)};">▸ KIT {i+1} OF {len(bundles)}</div>'
            f'<h3 style="font-size:1.15rem;margin-bottom:.3rem;">{esc(ico)} {esc(kit["title"])}</h3>'
            f'<p class="or-mini-body" style="margin-bottom:.8rem;font-style:italic;color:var(--muted);">'
            f'{esc(kit.get("outcome",""))}</p>'
            f'<div style="margin-bottom:.7rem;">{sample_html}</div>'
            f'{more_html}'
            f'</div>'
        )
    st.markdown(
        f'<div class="or-bento-mini or-reveal" '
        f'style="grid-template-columns:repeat(2,1fr);margin-bottom:2rem;">{kit_cells}</div>',
        unsafe_allow_html=True,
    )

    # ── Secondary layer divider ──
    st.markdown(
        '<div style="margin:2rem 0 1rem;display:flex;align-items:center;gap:1rem;">'
        '<span style="flex:1;height:1px;background:var(--border);"></span>'
        '<span style="font-family:JetBrains Mono,monospace;font-size:.65rem;'
        'letter-spacing:.18em;text-transform:uppercase;color:var(--muted);">'
        'FULL BIBLE · 1,137 PROMPTS · POWER-USER FILTERS BELOW</span>'
        '<span style="flex:1;height:1px;background:var(--border);"></span>'
        '</div>',
        unsafe_allow_html=True,
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
