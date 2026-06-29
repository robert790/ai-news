"""Streamlit UI for OpenRadar · v2.1.

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
from typing import Optional
from zoneinfo import ZoneInfo
import sys
from pathlib import Path
import random

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
    render_skill_tree,
    get_chapter,
    get_all_chapters,
    DOMAIN_META,
    COMPLEXITY_META,
)
import config
from theme import render_css, COLORS, SECTION_ACCENT
from tips import TIPS as ALL_TIPS
from prompts import (
    load_prompt_bible,
    filter_prompts,
    category_label,
    category_icon,
    category_color,
    difficulty_label,
    difficulty_color,
    all_categories,
    all_difficulties,
    all_model_ids,
)


# ===== Page config =====
st.set_page_config(
    page_title="OpenRadar",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(render_css(), unsafe_allow_html=True)

# Background overlays — radar pulse rings + scan line
# Both are fixed-position with pointer-events: none, sit behind content (z-index 0)
st.markdown(
    '<div class="bg-radar"></div>'
    '<div class="bg-scan"></div>',
    unsafe_allow_html=True,
)


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


def section_header(title: str, caption: str = ""):
    """Render the consistent section header. Used in every section.

    Brackets are rendered inline so they always sit adjacent to the title
    (CSS pseudo-elements get stretched by block-level h1 layout). Pass
    `caption=""` to skip the caption line entirely (use when caption
    lives somewhere else on the page, e.g. inside `.top-bar-right`).
    """
    cap_html = f'<p class="caption">{caption}</p>' if caption else ""
    st.markdown(
        f'<div class="section-header reveal-1">'
        f'<h1><span class="bracket">[</span> {title} <span class="bracket">]</span></h1>'
        f'{cap_html}'
        f'</div>',
        unsafe_allow_html=True,
    )


def subhead(label: str, color: str = "muted"):
    """Small uppercase label above content blocks. Optional accent color."""
    st.markdown(
        f'<div class="subsection-label reveal-1" style="color: var(--{color});">{label}</div>',
        unsafe_allow_html=True,
    )


def column_header(label: str, icon: str, count: int, color: str) -> None:
    """Render a prominent column header for the Azi landing page.

    Used at the top of each column to make the section structure obvious.
    Shows icon, label, count, and an accent line in the column's color.

    Args:
        label:  the column name (e.g., "News", "Tools", "Jobs")
        icon:   single emoji that represents the column
        count:  number of items currently in the column
        color:  hex color used for the label and bottom accent line
    """
    count_text = f"{count} {'item' if count == 1 else 'items'}"
    st.markdown(
        f'<div style="display: flex; align-items: baseline; gap: 0.6rem; '
        f'padding-bottom: 0.7rem; margin-bottom: 1rem; '
        f'border-bottom: 2px solid {color};">'
        f'<span style="font-size: 1.4rem;">{icon}</span>'
        f'<span style="font-family: Newsreader, serif; font-size: 1.5rem; '
        f'font-weight: 600; color: {color}; line-height: 1;">{label}</span>'
        f'<span style="font-family: JetBrains Mono, monospace; font-size: 0.65rem; '
        f'color: #8a8478; letter-spacing: 0.08em; text-transform: uppercase; '
        f'margin-left: auto;">{count_text}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )


def live_badge(text: str = "LIVE") -> None:
    """Render a pulsing LIVE indicator badge. Used on data feed sections."""
    st.markdown(
        f'<span class="live-badge">'
        f'<span class="status-dot"></span>{text}'
        f'</span>',
        unsafe_allow_html=True,
    )


SUMMARY_TRUNCATE_LIMIT = 140  # chars shown in card summary


def or_card(
    label: str,
    label_color: str,
    title: str,
    title_url: "Optional[str]" = None,
    summary: str = "",
    meta: str = "",
    meta_html: "Optional[str]" = None,
) -> None:
    """Render a clean Apple-inspired card.

    Single hairline border, generous padding, no top-accent line,
    no transform on hover (was breaking scroll). Use this in place of
    `st.container(border=True)` for cards on landing pages.

    Args:
        label: small uppercased tag (e.g. "▸ HN FEED").
        label_color: "coral" | "sky" | "sage" | "lavender" | "muted".
        title: card title — auto-escaped.
        title_url: optional external link.
        summary: optional body text — auto-escaped, auto-truncated.
        meta: plain-text meta line (HackerNews · ⬆ 209 · 2d ago) — auto-escaped.
        meta_html: optional raw HTML for the meta line (use instead of `meta`
            if you need markup like the Jobs score). Caller is responsible
            for escaping user data in the HTML.
    """
    def esc(s: str) -> str:
        return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    if title_url:
        title_block = (
            f'<a class="or-card-link" href="{esc(title_url)}" target="_blank">'
            f'<span class="or-card-title">{esc(title)}</span></a>'
        )
    else:
        title_block = f'<span class="or-card-title">{esc(title)}</span>'

    if summary:
        s_trim = summary[: SUMMARY_TRUNCATE_LIMIT]
        suffix = "…" if len(summary) > SUMMARY_TRUNCATE_LIMIT else ""
        summary_block = f'<p class="or-card-summary">{esc(s_trim)}{suffix}</p>'
    else:
        summary_block = ""

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
        f'{summary_block}'
        f'{meta_block}'
        f'</div>',
        unsafe_allow_html=True,
    )


def _build_tip_lines(n: int = 4, seed_key: str = "tips_strip_v1") -> str:
    """Pick `n` random tips once per session (stable) and emit the
    cycling `.tip-line` HTML. Returns a string so callers can wrap it
    in any container (corner pill, top-of-page bar, etc.) without
    Streamlit injecting a wrapper `<div>`.
    """
    if seed_key not in st.session_state:
        rng = random.Random()
        rng.seed()  # OS entropy
        st.session_state[seed_key] = rng.sample(ALL_TIPS, min(n, len(ALL_TIPS)))

    picked = st.session_state[seed_key]

    rows: list[str] = []
    for cat, body, _attrib in picked:
        body_esc = (
            body.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
        )
        rows.append(
            f'<div class="tip-line">'
            f'<span class="tips-cat {cat}">{cat}</span>'
            f'<span class="body">{body_esc}</span>'
            f'</div>'
        )
    return "".join(rows)


def _tips_corner_html(n: int = 4, seed_key: str = "tips_strip_v1") -> str:
    """Compact cycling dev-tip pill (used inside `.top-bar-right`)."""
    return (
        '<div class="tips-corner" aria-label="developer tip">'
        '<span class="tips-icon">tip</span>'
        '<div class="tips-slot">'
        + _build_tip_lines(n=n, seed_key=seed_key) +
        '</div>'
        '</div>'
    )


def _tips_top_html(n: int = 4, seed_key: str = "tips_strip_v1") -> str:
    """Wider cycling dev-tip bar for the top of a section. Same cycling
    animation as the corner pill, but stretches full-width and a touch
    larger so it reads as a primary surface instead of a chip.
    """
    return (
        '<div class="tips-top" aria-label="developer tip">'
        '<span class="tips-icon">tip</span>'
        '<div class="tips-slot-top">'
        + _build_tip_lines(n=n, seed_key=seed_key) +
        '</div>'
        '</div>'
    )


def tips_top(n: int = 4, seed_key: str = "tips_strip_v1") -> None:
    """Render the dev-tip bar at the TOP of the section, full-width."""
    st.markdown(_tips_top_html(n=n, seed_key=seed_key), unsafe_allow_html=True)


def top_bar(
    left_html: str,
    right_html: str = "",
    seed_key: str = "tips_corner_v1",
) -> None:
    """Render a horizontal bar. By default the right side hosts the cycling
    dev-tip pill, but pass `right_html` to override (e.g., put the section
    caption there instead). Whole bar is one HTML string so Streamlit
    doesn't wrap the inner pieces in their own `<div>`.
    """
    right_content = right_html or _tips_corner_html(seed_key=seed_key)
    html = (
        '<div class="top-bar reveal-1">'
        f'<div class="top-bar-left">{left_html}</div>'
        f'<div class="top-bar-right">{right_content}</div>'
        '</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def tips_strip(n: int = 4, seed_key: str = "tips_strip_v1") -> None:
    """Standalone dev-tip pill (full-width variant). Prefer `tips_top()`
    for the page-top placement, or `top_bar()` for the corner placement.
    """
    st.markdown(_tips_top_html(n=n, seed_key=seed_key), unsafe_allow_html=True)


# ===== Sidebar =====
now = datetime.now(ZoneInfo("Europe/Bucharest"))
date_short = now.strftime("%a %d %b").lower()
status_html = (
    '<span style="color: var(--sage);">● Groq connected</span>'
    if config.has_llm()
    else '<span style="color: var(--muted-2);">⚠ demo</span>'
)

# Session state defaults
if "selected_chapter" not in st.session_state:
    st.session_state.selected_chapter = "ch1"

with st.sidebar:
    # Top status bar — system tray
    st.markdown(
        '<div class="sb-statusbar">'
        '<span class="sb-status-name">▣ Open Radar</span>'
        '<span class="sb-version">v2.1</span>'
        '</div>',
        unsafe_allow_html=True,
    )

    # BRAND frame — crosshair cluster + name + tagline
    st.markdown(
        '<div class="sb-frame-label" data-frame="brand">'
        '<span class="bracket">┌──</span>[ BRAND ]<span class="bracket">──┐</span>'
        '</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="sb-frame">'
        '<div class="sb-cluster">'
        '<span class="c">⊕</span><span class="c">⊕</span><span class="c">⊕</span>'
        '<span class="c">⊕</span><span class="c center">⊕</span><span class="c">⊕</span>'
        '<span class="c">⊕</span><span class="c">⊕</span><span class="c">⊕</span>'
        '</div>'
        '<div class="sb-brand">'
        '<svg width="18" height="18" viewBox="0 0 20 20" class="crosshair">'
        '<circle cx="10" cy="10" r="7" fill="none" stroke="#a8c0ae" stroke-width="1" opacity="0.55"/>'
        '<line x1="10" y1="0" x2="10" y2="20" stroke="#a8c0ae" stroke-width="1" opacity="0.45"/>'
        '<line x1="0" y1="10" x2="20" y2="10" stroke="#a8c0ae" stroke-width="1" opacity="0.45"/>'
        '<circle cx="10" cy="10" r="1.6" fill="#a8c0ae"/>'
        '</svg>'
        '<h2>OpenRadar</h2>'
        '</div>'
        '<div class="tagline">OSINT signal feed · since 2026</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    # SECTIONS frame label
    st.markdown(
        '<div class="sb-frame-label" data-frame="sections">'
        '<span class="bracket">┌──</span>[ SECTIONS ]<span class="bracket">──┐</span>'
        '</div>',
        unsafe_allow_html=True,
    )

    SECTION = st.radio(
        "Navigate",
        options=["azi", "news", "learning", "jobs", "prompts"],
        format_func={
            "azi":      "☀  AZI",
            "news":     "📡  NEWS",
            "learning": "📚  LEARNING",
            "jobs":     "💼  JOBS",
            "prompts":  "🛠  PROMPTS",
        }.get,
        index=0,
        label_visibility="hidden",
        key="section",
    )

    # TELEMETRY frame — coordinate readouts + cache bar
    st.markdown(
        '<div class="sb-frame-label" data-frame="telemetry">'
        '<span class="bracket">┌──</span>[ TELEMETRY ]<span class="bracket">──┐</span>'
        '</div>',
        unsafe_allow_html=True,
    )
    cache_filled = "█" * 7
    cache_empty = "░" * 3
    st.markdown(
        f'<div class="sb-frame">'
        f'<div class="sb-telemetry-row"><span class="k">LAT</span><span class="v">44.4268°N</span></div>'
        f'<div class="sb-telemetry-row"><span class="k">LON</span><span class="v">26.1025°E</span></div>'
        f'<div class="sb-telemetry-divider"></div>'
        f'<div class="sb-telemetry-row"><span class="k">DATE</span><span class="v">{date_short}</span></div>'
        f'<div class="sb-telemetry-row"><span class="k">SESSION</span><span class="v">ops-7a3f</span></div>'
        f'<div class="sb-telemetry-row"><span class="k">CACHE</span>'
        f'<span class="sb-cache-bar"><span class="bar">{cache_filled}<span class="empty">{cache_empty}</span></span>'
        f'<span class="pct">67%</span></span></div>'
        f'<div class="sb-telemetry-row"><span class="k">STATUS</span><span class="v">'
        f'<span class="status-dot"></span>ONLINE</span></div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # ACTIVITY frame — recent ops log with timestamps, durations, color-coded status
    activity_rows = [
        # (HH:MM:SS, op_name, duration, status: ok | running | error)
        ("02:14:32", "hn.fetch()",       "124ms", "ok"),
        ("02:14:30", "repos.sync()",     " 89ms", "ok"),
        ("02:14:18", "hf.papers.load()", "312ms", "ok"),
        ("02:14:15", "lobsters.fetch()", " 67ms", "ok"),
        ("02:14:08", "session.start",    "   ──", "running"),
    ]
    status_icon = {"ok": "✓", "running": "⋯", "error": "✗"}
    status_class = {"ok": "status-ok", "running": "status-running", "error": "status-error"}
    rows_html = "".join(
        f'<div class="sb-activity-row">'
        f'<span class="time">{t}</span>'
        f'<span class="op">▸ {op}</span>'
        f'<span class="dur">{dur}</span>'
        f'<span class="status {status_class[st]}">{status_icon[st]}</span>'
        f'</div>'
        for t, op, dur, st in activity_rows
    )
    ops_count = len(activity_rows)
    st.markdown(
        f'<div class="sb-frame-label" data-frame="activity">'
        f'<span class="bracket">┌──</span>[ ACTIVITY ]<span class="bracket">──┐</span>'
        f'<span class="sb-counter">· {ops_count} OPS</span>'
        f'</div>',
        unsafe_allow_html=True,
    )
    st.markdown(f'<div class="sb-frame">{rows_html}</div>', unsafe_allow_html=True)

    # ACTIONS frame — quick action buttons
    st.markdown(
        '<div class="sb-frame-label" data-frame="actions">'
        '<span class="bracket">┌──</span>[ ACTIONS ]<span class="bracket">──┐</span>'
        '</div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="sb-frame"><div class="sb-action">', unsafe_allow_html=True)
    if st.button("↻  Refresh feeds", key="refresh_feeds", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    st.markdown('</div><div class="sb-action">', unsafe_allow_html=True)
    if st.button("⌘  Copy URL", key="copy_url", use_container_width=True):
        st.toast("URL: https://huggingface.co/spaces/vrobert94/ai-news")
    st.markdown('</div><div class="sb-action">', unsafe_allow_html=True)
    if st.button("⤴  Open in new tab", key="open_new_tab", use_container_width=True):
        st.markdown(
            '<script>window.open("https://huggingface.co/spaces/vrobert94/ai-news", "_blank");</script>',
            unsafe_allow_html=True,
        )
    st.markdown('</div></div>', unsafe_allow_html=True)

    # Footer
    st.markdown(
        '<div class="sb-footer">━━━ OpenRadar ━━━</div>',
        unsafe_allow_html=True,
    )


# =====================================================================
# SECTION: AZI — daily brief
# =====================================================================
if SECTION == "azi":

    # 1. Top of section: wider cycling dev-tip bar (prominent, full-width).
    tips_top(n=4)

    # 2. Section header. Caption lives inside `.top-bar-right` instead of
    #    under the h1, so we pass an empty string here.
    section_header("Azi", "")

    # 3. Top bar: LIVE FEED badge on the left, renamed caption on the right.
    #    "Bei cafeaua, scanezi lumea, pleci la treaba" replaces the older
    #    "Bea cafeaua, scanează lumea, pleci la treabă."
    top_bar(
        left_html='<span class="live-badge"><span class="status-dot"></span>LIVE FEED</span>',
        right_html='<span class="top-bar-caption">'
                   'Top 3 din fiecare. Bei cafeaua, scanezi lumea, pleci la treaba.'
                   '</span>',
    )

    col_news, col_tools, col_jobs = st.columns(3, gap="medium")

    with col_news:
        hn = load_hn() or []
        top3 = hn[:3]
        column_header("News", "📡", len(top3), "#e8a598")
        for item in top3:
            summary = (item.summary or "")[:SUMMARY_TRUNCATE_LIMIT]
            or_card(
                label="▸ HN FEED",
                label_color="coral",
                title=item.title[:90],
                title_url=item.url,
                summary=summary,
                meta=f"HackerNews · ⬆ {item.score} · {fmt_date(item.published_at)}",
            )

    with col_tools:
        # Prefer findarepo (curated 7-day growth deltas). Fallback to GitHub
        # Trending today if findarepo returns empty (network hiccup, scrape
        # miss, transient failure). Either way, normalize into a common
        # card-friendly dict so or_card renders cleanly.
        repos = load_repos() or []
        if repos:
            top3 = [
                {
                    "title": r.full_name,
                    "summary": r.description,
                    "url": r.url,
                    "stars": r.stars,
                    "growth": f"+{r.growth}/7d",
                    "language": r.language,
                    "source": "findarepo",
                }
                for r in repos[:3]
            ]
        else:
            gh = load_github() or []
            top3 = [
                {
                    "title": it.title,
                    "summary": it.summary or "",
                    "url": it.url,
                    "stars": f"{it.score}",
                    "growth": "today",
                    "language": (it.tags[0] if it.tags else "—").upper(),
                    "source": "GitHub Trending",
                }
                for it in gh[:3]
            ]
        column_header("Tools", "⭐", len(top3), "#a5c5d4")
        for t in top3:
            or_card(
                label=f"▸ {t['source']}",
                label_color="sky",
                title=t["title"][:90],
                title_url=t["url"],
                summary=t["summary"],
                meta=f"★ {t['stars']} · ↗ {t['growth']} · {t['language']}",
            )

    with col_jobs:
        mock_jobs = [
            {"title": "LLM Engineer", "company": "DRUID AI", "location": "Bucharest", "match": "82%"},
            {"title": "AI Product Manager", "company": "Bitdefender", "location": "Bucharest", "match": "76%"},
            {"title": "AI Solutions Consultant", "company": "ClusterPower", "location": "Iași", "match": "71%"},
        ]
        column_header("Jobs", "💼", len(mock_jobs), "#a8c0ae")
        for j in mock_jobs:
            or_card(
                label="▸ MATCH",
                label_color="sage",
                title=j["title"],
                summary=f"{j['company']} · 📍 {j['location']}",
                meta_html=f'<span class="or-card-score">{j["match"]}</span> match score',
            )
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
# SECTION: LEARNING — Skill tree (v0.4)
# =====================================================================
elif SECTION == "learning":

    section_header(
        "Learning",
        "AI Road · skill tree. De la fundație la advanced. Click un nod.",
    )

    subhead("Cele 15 capitole", "muted")

    # Skill tree visualization (Cytoscape.js)
    selected_id = render_skill_tree()

    # Initialize / update selection state
    if selected_id and selected_id in [ch.id for ch in get_all_chapters()]:
        st.session_state.selected_chapter = selected_id
    selected_id = st.session_state.get("selected_chapter", "ch1")

    # --- Chapter detail panel ---
    ch = get_chapter(selected_id)
    domain_meta = DOMAIN_META[ch.domain]
    complexity_meta = COMPLEXITY_META[ch.complexity]

    st.markdown(
        f'<a id="chapter-detail"></a>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div style="margin-top: 2.5rem;">'
        f'<div style="display: flex; align-items: center; gap: 0.8rem; margin-bottom: 0.5rem;">'
        f'<div style="font-family: Newsreader, serif; font-size: 2rem; '
        f'color: {domain_meta["color"]}; line-height: 1;">{ch.number:02d}</div>'
        f'<div style="font-family: JetBrains Mono, monospace; font-size: 0.7rem; '
        f'color: {domain_meta["color"]}; letter-spacing: 0.08em; text-transform: uppercase;">'
        f'{domain_meta["icon"]} {domain_meta["label"]} · {complexity_meta["label"]}'
        f'</div>'
        f'</div>'
        f'<h2 style="margin-top: 0.25rem; margin-bottom: 0.3rem;">{ch.title}</h2>'
        f'<p style="font-family: Newsreader, serif; font-style: italic; color: var(--muted); '
        f'font-size: 1.05rem; margin: 0;">{ch.subtitle}</p>'
        f'</div>',
        unsafe_allow_html=True,
    )

    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

    cols = st.columns([3, 1])
    with cols[0]:
        with st.container(border=True):
            st.markdown(ch.blurb)

            # Methods (BLUE-inspired v0.5)
            if ch.methods:
                st.markdown(
                    f'<div style="height: 0.6rem;"></div>',
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f'<div style="font-family: JetBrains Mono, monospace; '
                    f'font-size: 0.7rem; color: var(--muted); '
                    f'letter-spacing: 0.08em; text-transform: uppercase; '
                    f'margin-bottom: 0.6rem;">'
                    f'Methods · {len(ch.methods)}'
                    f'</div>',
                    unsafe_allow_html=True,
                )
                for m in ch.methods:
                    if m.recommended:
                        marker = "◆"
                        name_color = domain_meta["color"]
                        badge = (
                            f'<span style="font-family: JetBrains Mono, monospace; '
                            f'font-size: 0.6rem; color: {domain_meta["color"]}; '
                            f'background: {domain_meta["color"]}1a; '
                            f'padding: 0.1rem 0.5rem; border-radius: 10px; '
                            f'margin-left: 0.5rem; letter-spacing: 0.06em;">'
                            f'MAIN</span>'
                        )
                    else:
                        marker = "○"
                        name_color = "#a8a094"
                        badge = ""
                    st.markdown(
                        f'<div style="margin-bottom: 0.9rem;">'
                        f'<div style="display: flex; align-items: baseline; '
                        f'gap: 0.5rem; margin-bottom: 0.25rem;">'
                        f'<span style="color: {name_color}; font-size: 0.9rem;">{marker}</span>'
                        f'<span style="font-family: Newsreader, serif; '
                        f'font-size: 1.05rem; color: {name_color}; '
                        f'font-weight: 500;">{m.name}</span>'
                        f'{badge}'
                        f'</div>'
                        f'<div style="font-family: Newsreader, serif; '
                        f'font-style: italic; color: #c4b9a7; '
                        f'font-size: 0.92rem; margin-left: 1.3rem; '
                        f'margin-bottom: 0.15rem;">{m.summary}</div>'
                        f'<div style="font-family: JetBrains Mono, monospace; '
                        f'font-size: 0.68rem; color: #8a8478; '
                        f'margin-left: 1.3rem; letter-spacing: 0.03em;">'
                        f'When: {m.when_to_use}'
                        f'</div>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )

            # Prerequisites
            if ch.prerequisites:
                prereq_links = " · ".join(
                    f"[{get_chapter(p).title[:40]}](#chapter-detail)"
                    for p in ch.prerequisites
                )
                st.markdown(
                    f'<div style="margin-top: 1rem; font-family: JetBrains Mono, monospace; '
                    f'font-size: 0.72rem; color: var(--muted); letter-spacing: 0.04em;">'
                    f'Necesită: {prereq_links}'
                    f'</div>',
                    unsafe_allow_html=True,
                )

            st.markdown("<div style='height: 0.6rem;'></div>", unsafe_allow_html=True)

            st.markdown(
                '<div style="display: flex; gap: 0.6rem; align-items: center; '
                'margin-top: 1rem;">'
                '<span style="font-family: JetBrains Mono, monospace; font-size: 0.7rem; '
                'color: var(--muted); letter-spacing: 0.06em; text-transform: uppercase;">'
                'Citește complet:</span>'
                f'<a href="../ai-beginners-guide/index.html#{ch.anchor}" target="_blank" '
                f'style="font-family: Inter, sans-serif; font-size: 0.85rem;">'
                f'→ Deschide capitolul {ch.number} în AI Road</a>'
                '</div>',
                unsafe_allow_html=True,
            )

    with cols[1]:
        with st.container(border=True):
            st.caption(
                f'<span style="color: {domain_meta["color"]}; font-family: JetBrains Mono, '
                f'monospace; font-size: 0.7rem; letter-spacing: 0.06em; text-transform: uppercase;">'
                f'{domain_meta["label"]}</span>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<p style="font-family: Newsreader, serif; font-style: italic; '
                f'color: var(--muted); margin-top: 0.4rem; font-size: 0.92rem; line-height: 1.5;">'
                f'{domain_meta["blurb"]}</p>',
                unsafe_allow_html=True,
            )

            st.markdown(
                f'<div style="margin-top: 1rem; padding-top: 0.8rem; '
                f'border-top: 1px solid var(--border); '
                f'font-family: JetBrains Mono, monospace; font-size: 0.72rem; '
                f'color: {complexity_meta["color"]};">'
                f'{complexity_meta["label"]}</div>',
                unsafe_allow_html=True,
            )

            # Path navigation — prev/next chapter
            all_chapters = sorted(get_all_chapters(), key=lambda c: c.number)
            idx = next((i for i, c in enumerate(all_chapters) if c.id == ch.id), 0)
            prev_ch = all_chapters[idx - 1] if idx > 0 else None
            next_ch = all_chapters[idx + 1] if idx < len(all_chapters) - 1 else None

            st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
            nav_cols = st.columns(2)
            with nav_cols[0]:
                if prev_ch:
                    if st.button(f"← {prev_ch.number}", key=f"prev-{ch.id}", use_container_width=True):
                        st.session_state.selected_chapter = prev_ch.id
                        st.rerun()
            with nav_cols[1]:
                if next_ch:
                    if st.button(f"{next_ch.number} →", key=f"next-{ch.id}", use_container_width=True):
                        st.session_state.selected_chapter = next_ch.id
                        st.rerun()

    # --- All chapters list (for those who want to scroll) ---
    st.markdown("<div style='height: 3rem;'></div>", unsafe_allow_html=True)
    st.markdown("#### Toate capitolele")
    st.caption("Sau click direct pe oricare pentru a-l deschide.")

    for c in get_all_chapters():
        domain = DOMAIN_META[c.domain]
        is_selected = (c.id == selected_id)
        border_color = "var(--border-strong)" if is_selected else "var(--border)"
        with st.container(border=True):
            cols = st.columns([1, 5, 1])
            with cols[0]:
                st.markdown(
                    f'<div style="font-family: Newsreader, serif; font-size: 1.6rem; '
                    f'color: {domain["color"]}; line-height: 1;">{c.number:02d}</div>',
                    unsafe_allow_html=True,
                )
            with cols[1]:
                st.markdown(f"**{c.title}**")
                st.caption(c.subtitle)
            with cols[2]:
                if st.button("Deschide", key=f"open-{c.id}", use_container_width=True):
                    st.session_state.selected_chapter = c.id
                    st.rerun()


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
# SECTION: PROMPTS — Prompt Bible (1137 prompts × 12 categories)
# =====================================================================
elif SECTION == "prompts":

    bible = load_prompt_bible()
    n_total = len(bible.prompts)
    cats = all_categories(bible)
    diffs = all_difficulties()
    models = all_model_ids(bible)

    # Pre-compute category counts so pills show "85" next to "Code"
    cat_counts = {c["id"]: 0 for c in bible.categories}
    for p in bible.prompts:
        c = p.get("category", "")
        if c in cat_counts:
            cat_counts[c] += 1
    diff_counts = {d: 0 for d in diffs}
    for p in bible.prompts:
        d = p.get("difficulty", "")
        if d in diff_counts:
            diff_counts[d] += 1

    section_header(
        "Prompts",
        f"{n_total} prompturi production-grade. Click pe categorie sau difficulty ca să filtrezi.",
    )

    # Search bar — full width, always visible
    text_q = st.text_input(
        "search",
        placeholder="Caută în titlu, tag-uri, conținut...",
        label_visibility="collapsed",
        key="prompts_search",
    )

    # --- Category pills ---
    st.markdown(
        '<div class="prompts-pills-label">Categorie</div>',
        unsafe_allow_html=True,
    )
    cat_labels = ["All"] + [
        f"{category_icon(bible, c)} {category_label(bible, c)} · {cat_counts[c]}"
        for c in cats
    ]
    # Pills return the selected labels; we need to map back to ids.
    cat_pills = st.pills(
        "categorii",
        options=cat_labels,
        selection_mode="multi",
        default=[],
        label_visibility="collapsed",
        key="prompts_cat_pills",
    )
    cat_pills = cat_pills or []
    selected_cats = []
    for label in cat_pills:
        if label == "All":
            continue
        # Match "<icon> <Label> · <count>" against our options
        for c in cats:
            expected = f"{category_icon(bible, c)} {category_label(bible, c)} · {cat_counts[c]}"
            if label == expected:
                selected_cats.append(c)
                break

    # --- Difficulty pills ---
    st.markdown(
        '<div class="prompts-pills-label">Difficulty</div>',
        unsafe_allow_html=True,
    )
    diff_pills = st.pills(
        "dificultate",
        options=[difficulty_label(d) for d in diffs],
        selection_mode="multi",
        default=[],
        label_visibility="collapsed",
        key="prompts_diff_pills",
    )
    selected_diffs = diff_pills or []

    # --- Model pills (16 — wrap in st.pills, will scroll horizontally) ---
    st.markdown(
        '<div class="prompts-pills-label">Modele</div>',
        unsafe_allow_html=True,
    )
    model_pills = st.pills(
        "modele",
        options=[bible.models.get(m, {}).get("label", m) for m in models],
        selection_mode="multi",
        default=[],
        label_visibility="collapsed",
        key="prompts_model_pills",
    )
    selected_models = []
    if model_pills:
        for label in model_pills:
            for m in models:
                if bible.models.get(m, {}).get("label", m) == label:
                    selected_models.append(m)
                    break

    # --- Sort + clear ---
    sort_cols = st.columns([3, 1], gap="small", vertical_alignment="center")
    with sort_cols[0]:
        sort_label = st.radio(
            "sort",
            options=["Default", "A→Z", "Beginner first", "Expert first"],
            horizontal=True,
            label_visibility="collapsed",
            key="prompts_sort",
        )
    with sort_cols[1]:
        any_active = bool(text_q or cat_pills or selected_diffs or selected_models)
        if any_active:
            if st.button("✕  Resetează filtre", key="prompts_reset", use_container_width=True):
                # Clear everything by setting session state
                for k in ["prompts_search", "prompts_cat_pills", "prompts_diff_pills",
                          "prompts_model_pills", "prompts_sort"]:
                    st.session_state[k] = [] if "pills" in k or k == "prompts_sort" else ""
                st.session_state["prompts_sort"] = "Default"
                st.rerun()

    # --- Compute results ---
    # For text + categories + diffs + models: use filter_prompts for text
    # and category. For multi-category, multi-difficulty, multi-model we
    # need a custom filter.
    results = []
    needle = text_q.strip().lower()
    for p in bible.prompts:
        if selected_cats and p.get("category") not in selected_cats:
            continue
        if selected_diffs and p.get("difficulty") not in selected_diffs:
            continue
        if selected_models and not any(m in p.get("models", []) for m in selected_models):
            continue
        if needle:
            haystack_parts = [
                p.get("title", ""),
                " ".join(p.get("tags", []) or []),
                p.get("when", ""),
                p.get("prompt", ""),
                " ".join(p.get("notes", []) or []),
            ]
            haystack = " ".join(haystack_parts).lower()
            if needle not in haystack:
                continue
        results.append(p)

    # Sort
    if sort_label == "A→Z":
        results = sorted(results, key=lambda p: p.get("title", "").lower())
    elif sort_label == "Beginner first":
        results = sorted(
            results,
            key=lambda p: diffs.index(p.get("difficulty", "intermediate")),
        )
    elif sort_label == "Expert first":
        results = sorted(
            results,
            key=lambda p: -diffs.index(p.get("difficulty", "intermediate")),
        )

    n = len(results)
    any_filter = bool(text_q or selected_cats or selected_diffs or selected_models)
    st.markdown(
        f'<div class="prompts-count">'
        f'<span class="num">{n}</span>'
        f'<span class="lbl">/{n_total} prompturi'
        f'{" · filtrat" if any_filter else ""}'
        f'</span></div>',
        unsafe_allow_html=True,
    )

    st.markdown("<div style='height: 0.6rem;'></div>", unsafe_allow_html=True)

    # --- Result cards ---
    if n == 0:
        st.markdown(
            '<div class="prompts-empty">'
            'Nimic pe filtre. Schimbă text sau categorie.'
            '</div>',
            unsafe_allow_html=True,
        )
    else:
        for p in results:
            cat_id = p.get("category", "")
            cat_label = category_label(bible, cat_id)
            cat_color = category_color(bible, cat_id)
            diff = p.get("difficulty", "intermediate")
            diff_color = difficulty_color(diff)

            title = p.get("title", "Untitled")
            when = p.get("when", "")
            tags = p.get("tags", []) or []
            pmodels = p.get("models", []) or []
            body = p.get("prompt", "")
            variants = p.get("variants") or {}
            notes = p.get("notes") or []
            anti = p.get("antiPatterns") or []

            # Header row: icon + title + badges
            tags_html = (
                "".join(
                    f'<span class="pb-tag">{t}</span>'
                    for t in tags[:6]
                )
            )
            models_html = (
                " · ".join(
                    bible.models.get(m, {}).get("label", m) for m in pmodels
                )
            )
            when_block = (
                f'<div class="pb-when">{when}</div>' if when else ""
            )
            tags_block = (
                f'<div class="pb-tags">{tags_html}</div>' if tags_html else ""
            )
            models_block = (
                f'<div class="pb-models">{models_html}</div>' if models_html else ""
            )

            st.markdown(
                f'<div class="pb-card">'
                f'<div class="pb-card-head">'
                f'<span class="pb-icon" style="color: {cat_color};">'
                f'{category_icon(bible, cat_id)}</span>'
                f'<span class="pb-title">{title}</span>'
                f'<span class="pb-cat" style="color: {cat_color}; border-color: {cat_color}33;">'
                f'{cat_label}</span>'
                f'<span class="pb-diff" style="color: {diff_color}; border-color: {diff_color}33;">'
                f'{difficulty_label(diff)}</span>'
                f'</div>'
                f'{when_block}'
                f'{tags_block}'
                f'{models_block}'
                f'</div>',
                unsafe_allow_html=True,
            )

            # Variant tabs (one per supported model variant)
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

            # Notes + AntiPatterns (collapsible expander)
            if notes or anti:
                with st.expander("Why it works · What breaks it", expanded=False):
                    if notes:
                        st.markdown("**Why it works**")
                        for n_line in notes:
                            st.markdown(f"- {n_line}")
                    if anti:
                        st.markdown("")
                        st.markdown("**What breaks it**")
                        for a_line in anti:
                            st.markdown(f"- {a_line}")

            st.markdown("<div style='height: 1.2rem;'></div>", unsafe_allow_html=True)


# ===== Footer =====
st.markdown(
    '<div style="border-top: 1px solid var(--border); padding-top: 1.5rem; margin-top: 4rem; '
    'font-family: JetBrains Mono, monospace; font-size: 0.7rem; '
    'color: var(--muted-2); text-align: center; letter-spacing: 0.04em;">'
    'OpenRadar · v2.1 · pentru ingineri care beau cafeaua cu ochii pe lume'
    '</div>',
    unsafe_allow_html=True,
)