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
from learning import (
    render_skill_tree,
    get_chapter,
    get_all_chapters,
    DOMAIN_META,
    COMPLEXITY_META,
)
import config
from theme import render_css, COLORS, SECTION_ACCENT


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


def section_header(title: str, caption: str):
    """Render the consistent section header. Used in every section.

    Brackets are rendered inline so they always sit adjacent to the title
    (CSS pseudo-elements get stretched by block-level h1 layout).
    """
    st.markdown(
        f'<div class="section-header reveal-1">'
        f'<h1><span class="bracket">[</span> {title} <span class="bracket">]</span></h1>'
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
            "azi":      "▸  Azi",
            "news":     "▸  News",
            "learning": "▸  Learning",
            "jobs":     "▸  Jobs",
            "prompts":  "▸  Prompts",
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

    section_header(
        "Azi",
        "Top 3 din fiecare. Bea cafeaua, scanează lumea, pleci la treabă.",
    )
    live_badge("LIVE FEED")

    col_news, col_tools, col_jobs = st.columns(3, gap="medium")

    with col_news:
        hn = load_hn() or []
        top3 = hn[:3]
        column_header("News", "📡", len(top3), "#e8a598")
        for item in top3:
            with st.container(border=True):
                st.markdown('<div class="card-label coral">▸ HN FEED</div>', unsafe_allow_html=True)
                st.markdown(f"**[{item.title[:90]}]({item.url})**")
                summary = (item.summary or "")[:140]
                if summary:
                    st.caption(summary + ("..." if len(item.summary or "") > 140 else ""))
                st.caption(f"HackerNews · ⬆ {item.score} · {fmt_date(item.published_at)}")

    with col_tools:
        repos = load_repos() or []
        top3 = repos[:3]
        column_header("Tools", "⭐", len(top3), "#a5c5d4")
        for r in top3:
            with st.container(border=True):
                st.markdown('<div class="card-label sky">▸ findarepo</div>', unsafe_allow_html=True)
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
        column_header("Jobs", "💼", len(mock_jobs), "#a8c0ae")
        for j in mock_jobs:
            with st.container(border=True):
                st.markdown('<div class="card-label">▸ MATCH</div>', unsafe_allow_html=True)
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
    'OpenRadar · v2.1 · pentru ingineri care beau cafeaua cu ochii pe lume'
    '</div>',
    unsafe_allow_html=True,
)