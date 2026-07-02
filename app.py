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

# Ambient radar/scan overlays were removed in PR15; .or-radar / .or-scan
# selectors are now stripped via `_STATIC_CSS` for any stray markup.

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

    Layout (PR16 header cleanup):
      ┌────────────┬────────────────────────────┬─────────┐
      │ brand      │ 5 button nav (single line) │ refresh │
      └────────────┴────────────────────────────┴─────────┘

    Brand block stacks "OpenRadar" + a one-line subtitle with `nowrap`
    + tight letter-spacing so the subtitle never wraps mid-phrase.
    Refresh action lives in the right column as a quiet text button.
    """
    if "section" not in st.session_state:
        # Allow `?section=learning` deep-link via query params
        _qp = st.query_params.get("section", "groq")
        _valid = {"groq", "news", "learning", "jobs", "prompts"}
        st.session_state.section = _qp if _qp in _valid else "groq"

    # Tighter column ratios so brand is compact, nav gets the room it
    # actually needs, and refresh button gets a narrow dedicated slot.
    cols = _columns([1.05, 3.55, 0.4], gap="small")

    # Brand — plain text identity. Subtitle uses non-breaking spaces
    # between dots so the phrase "AI tools · prompts · learn · jobs"
    # never wraps mid-phrase on a desktop viewport. CSS .or-name-kicker
    # enforces nowrap + tight letter-spacing.
    with cols[0]:
        st.markdown(
            '<a class="or-topnav-brand" href="?section=groq">'
            '<span class="or-name-stack">'
            '<span class="or-name">OpenRadar</span>'
            '<span class="or-name-kicker">AI&nbsp;tools&nbsp;·&nbsp;prompts&nbsp;·&nbsp;learn&nbsp;·&nbsp;jobs</span>'
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
            ("groq",     "Home"),
            ("news",     "Tools"),
            ("prompts",  "Prompt Kits"),
            ("learning", "Learn"),
            ("jobs",     "Jobs"),
        ]
        st.markdown('<div class="or-nav-shell">', unsafe_allow_html=True)
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

    # Quiet refresh action — narrow column, no icon, just a plain
    # text button. Clears Streamlit cache and reruns. Visually quiet
    # so the header reads as a workbench chrome, not a dashboard
    # toolbar.
    with cols[2]:
        if st.button("Refresh", key="nav_refresh", use_container_width=True,
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


# ─── PR15: static functional section content ────────────────────────────
# Each static item: (key, label, title, body, detail_dict). The detail dict
# carries the spec-required fields per section so a single render helper can
# drive any of the four sections. Pure local content — no live data, no
# scraping, no fake telemetry.
_STATIC_TOOLS = [
    ("coding",
     "Build",
     "Coding assistants",
     "Repo-aware help for edits, tests, refactors, and review.",
     {
        "what": "Editors and chat tools that read your repository, follow "
                "your project rules, and respond with code that fits your "
                "stack and style.",
        "best_for": "Day-to-day coding work: writing functions, debugging, "
                    "writing tests, refactors, code review, and reading "
                    "unfamiliar code with explanations.",
        "when": "Use when you write or modify code most days and want fewer "
                "context switches between your editor and a separate chat.",
        "when_not": "Avoid for high-stakes production changes that touch "
                    "auth, billing, or shared infra without a human review "
                    "step. The assistant helps you move faster; it does not "
                    "replace code review.",
        "checklist": [
            "Pick one assistant that supports your editor and language stack.",
            "Wire project memory or rules so the assistant knows your style.",
            "Start every task with a short scope note: files, goals, risks.",
            "Run the assistant's diff through your own review before merge.",
            "Treat generated tests as a draft, not a guarantee.",
        ],
        "compare": "Editor integration, repo context size, supported "
                   "languages, pricing model, and whether it can run tests "
                   "in-place. Pick the one you can leave open all day.",
        "related": "Related signals below — repos, papers, and discussions.",
     }),
    ("research",
     "Decide",
     "Research tools",
     "Turn many sources into a clearer decision.",
     {
        "what": "Readers and summarizers that turn long sources — papers, "
                "articles, threads, transcripts, docs — into a short list "
                "of points you can act on.",
        "best_for": "Decisions where the input is bigger than your time "
                    "to read it: vendor selection, market scan, "
                    "literature review, internal-doc summarization.",
        "when": "Use when you have at least three sources to compare, or "
                "when one source is more than ~10 pages and the question "
                "is specific.",
        "when_not": "Avoid for anything where one wrong claim causes real "
                    "harm (legal, medical, financial). Treat the output as "
                    "a pointer to the source, not the source itself.",
        "checklist": [
            "Write down the 2–3 questions you actually need answered.",
            "Pick sources that disagree — a single feed is not research.",
            "Force a written summary per source before comparing them.",
            "Capture exact quotes for any claim you intend to repeat.",
            "End with a one-paragraph decision and the evidence behind it.",
        ],
        "compare": "Input formats accepted, citation behavior, freshness "
                   "of the index, privacy of uploaded docs, and how it "
                   "handles conflicting sources.",
        "related": "Related signals below — papers, threads, and analysis.",
     }),
    ("media",
     "Create",
     "Image/video tools",
     "Generate, edit, storyboard, or repurpose visual material.",
     {
        "what": "Tools that generate, edit, restyle, storyboard, or "
                "repurpose images and short videos from a written brief "
                "or an existing asset.",
        "best_for": "Visual assets that are needed faster than a designer "
                    "can hand-draft them: blog hero images, social "
                    "thumbnails, product mockups, rough storyboards, "
                    "format-conversion edits.",
        "when": "Use when the project can tolerate 'good enough now, "
                "polish later', or when you need 5–10 variants to compare.",
        "when_not": "Avoid for final legal-grade assets, anything with "
                    "named people or trademarked brands without review, "
                    "and any image that needs precise type or layout.",
        "checklist": [
            "Start from a written brief: subject, mood, constraints, "
            "must-not-include list.",
            "Generate 3–5 variants and pick the strongest direction.",
            "Run final output through your brand and accessibility check.",
            "Reuse a small set of prompts; rotate when quality drifts.",
            "Keep the source files (seeds, masks) so edits stay reproducible.",
        ],
        "compare": "Style consistency across runs, editability of the "
                   "output (layers, masks, raw seeds), license terms for "
                   "generated assets, and cost per asset.",
        "related": "Related signals below — fresh media tools worth scanning.",
     }),
    ("agents",
     "Operate",
     "Productivity agents",
     "Automate inboxes, docs, spreadsheets, meetings, and repetitive admin.",
     {
        "what": "Agents that connect to inboxes, documents, calendars, "
                "spreadsheets, ticketing, and meeting tools to do small "
                "jobs end-to-end with some autonomy.",
        "best_for": "Repetitive, low-risk tasks you can describe in one "
                    "sentence: 'move emails matching X into folder Y', "
                    "'summarize this thread into a doc', 'fill this "
                    "spreadsheet from these PDFs'.",
        "when": "Use when the task is small enough that a wrong answer "
                "costs less than the time you save. Keep humans in the "
                "loop for anything with side effects.",
        "when_not": "Avoid for first-touch actions on accounts, anything "
                    "that sends money, and anything where the failure mode "
                    "is silent (no log, no notification).",
        "checklist": [
            "Start with read-only access — never write on day one.",
            "Define a clear done-condition and a stop rule.",
            "Log every action the agent took; review the log weekly.",
            "Promote to write access only after two clean weeks.",
            "Keep a kill switch: a way to revoke access in one step.",
        ],
        "compare": "Which apps it can connect to, how it surfaces "
                   "uncertainty, audit log quality, and what happens when "
                   "a step fails halfway through a multi-step run.",
        "related": "Related signals below — workflow and agent picks.",
     }),
]

_STATIC_PROMPTS = [
    ("ship",
     "Build",
     "Ship a feature safely",
     "Scope files, risks, tests, review, and rollback before merge.",
     {
        "use_case": "Reduce the failure modes when shipping a non-trivial "
                    "change. Forces scope, risk, and rollback to be decided "
                    "before any code is written.",
        "inputs": "Feature name or ticket id, the user-visible behavior "
                  "you are changing, and any system it touches.",
        "starter": "I'm about to change <scope>. Before writing code, "
                   "list: (1) the files this change must touch, (2) the "
                   "risks I should pre-empt, (3) the tests I must add or "
                   "update, and (4) a one-line rollback plan. Ask me "
                   "anything that is unclear before you start.",
        "when": "Use at the start of any feature branch that touches more "
                "than two files, any shared system, or anything that "
                "changes a contract.",
        "when_not": "Skip for tiny one-line fixes and obvious typo "
                    "corrections; the checklist overhead is larger than "
                    "the risk.",
        "quality": "A good run ends with four numbered lists, no "
                   "ambiguity in 'done', and an explicit rollback line "
                   "(feature flag off, revert commit, or safe migration).",
        "next": "Treat the AI's output as a checklist; do not skip the "
                "rollback line. Paste the four lists into the PR "
                "description so the reviewer can scan them.",
     }),
    ("compare",
     "Decide",
     "Compare AI tools",
     "Score options by use case, cost, quality, risk, and switching cost.",
     {
        "use_case": "Pick between two or more AI tools when there is no "
                    "obvious default and the decision will be revisited "
                    "in the next quarter.",
        "inputs": "The 2–4 candidate tools, the specific use case, "
                  "the team size that will use it, and any existing "
                  "tools it must integrate with.",
        "starter": "Compare <tool A> and <tool B> for <use case>. Score "
                   "each on: fit, cost per month, output quality, "
                   "latency, integration effort, data privacy, and "
                   "switching cost. End with one recommendation and "
                   "the top three reasons. Flag any assumption you "
                   "made.",
        "when": "Use when the team is asking 'should we switch?' and "
                "the answer is not yet obvious from the marketing "
                "pages.",
        "when_not": "Skip for tools you will touch once. The scorecard "
                    "overhead is only worth it for repeated use.",
        "quality": "A good run produces numeric or at least ordered "
                   "scores per criterion, makes its assumptions explicit, "
                   "and names the single criterion that drove the "
                   "decision.",
        "next": "Save the scorecard in a shared doc. Re-run it in "
                "three months — most 'switch' decisions are easier "
                "to defend the second time.",
     }),
    ("learn",
     "Learn",
     "Learn a concept",
     "Explain with examples, checks for understanding, and practice tasks.",
     {
        "use_case": "Pick up a new AI concept fast and verify the "
                    "explanation with a concrete check, not just by "
                    "reading.",
        "inputs": "The concept name, your current level (beginner / "
                  "intermediate / applied), and the problem you are "
                  "trying to solve.",
        "starter": "Explain <concept> as if I am a senior engineer who "
                   "has never worked on AI. Give one worked example, "
                   "one common misconception, and one 10-minute "
                   "practice task. Then ask me one question to check "
                   "I understood.",
        "when": "Use before a meeting, interview, or decision that "
                "touches a topic you have only heard about.",
        "when_not": "Skip for foundational concepts you can already "
                    "explain in one sentence — you'll get a textbook "
                    "answer instead of a useful one.",
        "quality": "A good run ends with: one concrete example (not "
                   "abstract), one specific misconception (not 'there "
                   "are some edge cases'), and a practice task that "
                   "fits in 10 minutes.",
        "next": "Do the practice task before declaring the concept "
                "'known'. If you cannot do it, ask for a second example.",
     }),
    ("outreach",
     "Write",
     "Write outreach",
     "Draft a specific message with context, value, proof, and a low-friction ask.",
     {
        "use_case": "Send cold or warm messages that actually get a "
                    "reply, instead of generic 'just checking in' "
                    "patterns that get archived.",
        "inputs": "Recipient name and role, what you know about them or "
                  "their company, the value you can offer, and the "
                  "specific ask (a 15-min call, a reply, an intro).",
        "starter": "Draft a 90-word message to <name> at <company> "
                   "about <specific topic>. Include: (1) one line of "
                   "context that shows you read their work, (2) one "
                   "concrete value you can offer, (3) one piece of "
                   "proof (a number, a customer, a public artifact), "
                   "(4) a low-friction ask. Keep the subject line "
                   "under 50 characters.",
        "when": "Use whenever the recipient is busy and the ask "
                "matters — first cold email, a re-engagement, a "
                "warm intro request.",
        "when_not": "Skip for transactional messages (meeting invite, "
                    "status update). The format is overhead when the "
                    "ask is mechanical.",
        "quality": "A good run names a specific thing the recipient "
                   "wrote or shipped, gives a concrete number or "
                   "artifact as proof, and offers a single ask — not "
                   "three.",
        "next": "Send 3 versions, pick the shortest that still says "
                "the right thing. If no reply in 5 business days, "
                "send one follow-up that adds new context, not a "
                "'bumping this up' nudge.",
     }),
]

_STATIC_LEARN = [
    ("basics",
     "Foundation",
     "AI basics",
     "Models, context, tokens, strengths, limits, and responsible use.",
     "ch2",   # jump-start chapter
     {
        "understand": "How modern language and multimodal models actually "
                      "work, what context and tokens mean in practice, "
                      "and where the model is reliable versus brittle.",
        "why": "Most user-facing mistakes come from assuming the model "
               "thinks like a person. Understanding tokens and context "
               "is what unlocks every other AI topic on this site.",
        "exercise": "Open any assistant and ask the same question "
                    "twice: once with 50 words of context and once "
                    "with 500. Note where the answer changed. That's "
                    "context in action.",
        "mistake": "Treating the model as a search engine. It generates "
                   "the most likely next token; it does not look up "
                   "facts unless you give it a tool to do so.",
        "next_chapter": "Chapter 2 — token economics and cost.",
        "next": "Pick one task you do weekly. Write a 5-bullet brief "
                "(what context the model needs, what a good answer "
                "looks like, what a bad one looks like). Save the "
                "brief as a template.",
     }),
    ("prompting",
     "Craft",
     "Prompting fundamentals",
     "Inputs, constraints, examples, verification, and iteration.",
     "ch3",
     {
        "understand": "How to design prompts that produce verifiable, "
                      "repeatable outputs instead of lucky one-shots.",
        "why": "The same prompt that gives a great result today can "
               "give a different one tomorrow. Prompting is the "
               "discipline of making the output predictable.",
        "exercise": "Take a prompt you already use. Add (1) one "
                    "explicit constraint, (2) one worked example, "
                    "(3) one verification step. Run the new and old "
                    "versions on three tasks and compare.",
        "mistake": "Adding more words until it works. Each extra "
                   "instruction adds noise; if the model is ignoring "
                   "a rule, isolate it and restate it more concretely.",
        "next_chapter": "Chapter 4 — verification and self-critique.",
        "next": "Keep a small prompt log: before, after, what changed, "
                "what got better. Patterns from 5 logs beat advice "
                "from 50 blog posts.",
     }),
    ("rag",
     "Grounding",
     "RAG basics",
     "Retrieval, chunking, citations, evaluation, and failure modes.",
     "ch7",
     {
        "understand": "How retrieval-augmented generation works end-to-end: "
                      "a question is matched against chunks of your own "
                      "documents, the top chunks are stuffed into the "
                      "model's context, and the model answers using them.",
        "why": "RAG is the difference between an assistant that knows "
               "your team and one that just sounds confident. The "
               "failure modes (bad chunks, missing citations, silent "
               "hallucination) are also where user trust breaks.",
        "exercise": "Pick a folder of your own notes or docs (30+ "
                    "files). Build a tiny RAG over them with any "
                    "off-the-shelf library. Log every question where "
                    "the answer looked right but the citation was "
                    "missing or wrong.",
        "mistake": "Trusting the answer without checking the cited "
                   "chunk. Bad citations are silent — the model "
                   "paraphrases confidently.",
        "next_chapter": "Chapter 6 — RAG evaluation basics.",
        "next": "Use the citation log as your next iteration input. "
                "Most RAG bugs are chunking bugs, not model bugs.",
     }),
    ("agents",
     "Systems",
     "Agent workflows",
     "Break tasks into tools, state, checks, handoffs, and recovery paths.",
     "ch8",
     {
        "understand": "How to break a real task into a workflow an AI "
                      "agent can run reliably, with explicit checks, "
                      "handoffs between steps, and a recovery rule for "
                      "each step.",
        "why": "A single-shot prompt is fine for 'summarize this'. A "
               "multi-step task with side effects (fetch, transform, "
               "write, notify) needs an agent workflow — and most "
               "agent failures come from missing recovery paths, not "
               "from bad models.",
        "exercise": "Pick a task you do weekly with at least 4 steps. "
                    "Write the steps as (tool, input, check, failure "
                    "path) tuples. Hand one tuple to an AI and see if "
                    "it can execute the step on its own.",
        "mistake": "Skipping the failure path. Every step needs an "
                   "explicit answer to 'what do we do if this "
                   "fails?' — retry, skip, escalate, or abort.",
        "next_chapter": "Chapter 8 — agent workflows in practice.",
        "next": "Treat the tuple list as the source of truth. Any "
                "new agent that wants to do part of the workflow "
                "inherits the same check and failure path.",
     }),
]

_STATIC_JOBS = [
    ("operator",
     "Role",
     "AI product operator",
     "Turn models and workflows into reliable business outcomes.",
     {
        "does": "Owns the translation from model capability to a shipped "
                "workflow that a real team uses every week. Drives "
                "rollout, evaluation, and adoption — not the model "
                "training itself.",
        "skills": ["Workflow design", "Evaluation basics", "Stakeholder demos", "Adoption metrics"],
        "proof": "Run a 30-day pilot with one team: define the workflow, "
                 "ship the assistant, measure usage and quality weekly, "
                 "and write up what worked, what didn't, and what you "
                 "shipped next.",
        "search_terms": ["AI product operator", "AI workflow lead", "AI solutions"],
        "warning": "Job postings that ask for 'prompt engineering plus "
                   "product' are often this role in disguise, but some "
                   "are 'build me a wrapper around a model and call it "
                   "a product'. Ask what shipped to users last quarter.",
     }),
    ("automation",
     "Automation",
     "AI automation specialist",
     "Connect tools, documents, workflows, and repetitive operations.",
     {
        "does": "Builds and maintains the connections between AI tools "
                "and the rest of the operations stack (docs, sheets, "
                "ticketing, CRM, internal databases). Usually the "
                "person who turns a one-off prompt into a workflow "
                "that runs every Monday morning.",
        "skills": ["Scripting", "API integration", "Workflow design", "Ops hygiene"],
        "proof": "Replace one recurring multi-tool task (e.g., weekly "
                 "report assembly, lead routing, ticket triage) with "
                 "an automated flow. Document the before / after "
                 "with a short Loom or doc.",
        "search_terms": ["AI automation specialist", "automation engineer", "workflow engineer"],
        "warning": "Roles that are really 'prompt monkey for a SaaS "
                   "tool' will not develop the engineering skills you "
                   "want. Ask how much of the work is wiring vs. "
                   "typing into a chat box.",
     }),
    ("designer",
     "Design",
     "Prompt/workflow designer",
     "Build reusable instructions, evaluations, and process templates.",
     {
        "does": "Packages repeatable procedures that other people can "
                "reuse safely. Owns the prompt library, the evaluation "
                "templates, and the process docs that go with them. "
                "Bridges engineering and the rest of the business.",
        "skills": ["Prompt design", "Evaluation design", "Documentation", "Review"],
        "proof": "Publish one prompt + evaluation template that two "
                 "different teams adopted without changes. Adoption, "
                 "not creation, is the proof.",
        "search_terms": ["prompt designer", "prompt engineer", "AI workflow designer"],
        "warning": "The 'prompt engineer' job title peaked in 2023 and "
                   "is now used loosely. Look for roles that mention "
                   "evaluation, internal documentation, or process "
                   "design — those are the real signal.",
     }),
    ("support",
     "Support",
     "AI developer tools support",
     "Help teams adopt coding assistants, agents, and model tooling.",
     {
        "does": "Helps engineering teams adopt coding assistants and "
                "agent tooling, debug integration issues, run "
                "enablement sessions, and turn field feedback into "
                "concrete improvements.",
        "skills": ["Developer tools", "Coding assistants", "Debugging", "Enablement"],
        "proof": "Run an internal enablement program for one team: "
                 "workshop, shared rules, weekly office hour, measured "
                 "adoption. The artifact is a written playbook "
                 "someone else can run.",
        "search_terms": ["developer relations", "developer tools support", "AI enablement"],
        "warning": "Roles that are pure customer-support ticket "
                   "queues won't develop the depth you want. Look for "
                   "titles that pair 'developer' with 'advocate', "
                   "'experience', or 'adoption'.",
     }),
]


# PR19: English surface layer for the 10-chapter Learn guide.
# Per the spec, at minimum we translate:
# - chapter titles
# - subtitles
# - intro paragraphs
# - verifier labels
# - method names + summaries
# - "build this" exercise lines
# - cross-ref labels
# - button labels (already English: Mark complete / Previous / Next)
# Body_md is intentionally NOT rendered in the English-first guide.
# Source of truth stays in `learning/learning_render._render_body_md`
# and `content/chapters.jsonl` — we just skip emitting it here so the
# visible Learn UI is 100% English. See the "Looking for more?"
# placeholder in `_render_english_chapter` for the user-facing note.
_LOCALIZE = {
    "ch1": {
        "title": "Why AI matters now",
        "subtitle": "From hand-written rules to models that simulate thinking. The seven eras.",
        "intro": "Before we touch a keyboard, take a step back — not to "
                 "become a historian, but to understand why the AI "
                 "world looks the way it does today.",
        "verifiers": [
            "I know modern AI means deep neural networks (deep learning).",
            "I know what the 2017 Transformer paper did and why it matters.",
            "I know that today's LLMs use the Transformer architecture.",
        ],
        "build_this": "Draw a timeline on paper with the seven eras. "
                      "Next to each, write a one-word keyword: rules, ML, "
                      "DL, Transformer, LLM, restrictions, fusion.",
        "method_name": "Timeline on the fridge",
        "method_summary": "Draw the timeline on A3 paper, each era as a "
                          "colored circle with a one-word keyword. Tape "
                          "it where you see it every day — fridge, monitor, door.",
        "method_when": "When you want context for tech news without searching.",
    },
    "ch2": {
        "title": "How an LLM thinks",
        "subtitle": "Patterns on 500 GB of text. It doesn't think — it predicts. And that's enough to sound like it does.",
        "intro": "An LLM doesn't think. It walks text by statistics. But it's "
                 "good enough to sound like it does. Here's how.",
        "verifiers": [
            "I know what a token is and how it's formed.",
            "I know what a context window is and why it matters.",
            "I know LLMs can 'hallucinate' and that I should verify the source.",
        ],
        "build_this": "Open any chat AI. Send: \"How many tokens does this "
                      "message have?\" Then send the same message with "
                      "temperature 0 vs 0.9. Note the difference.",
        "method_name": "Token detective",
        "method_summary": "Take 10 sentences from your own life (emails, "
                          "messages, notes). Run them through a tokenizer "
                          "(platform.openai.com/tokenizer). Count tokens per sentence.",
        "method_when": "When you want to understand why one prompt costs more than another.",
    },
    "ch3": {
        "title": "Prompting fundamentals",
        "subtitle": "Talk to the AI like a manager with a new colleague: clear, structured, with examples.",
        "intro": "The difference between a bad prompt and a good one is a "
                 "few hours of work saved per day. Prompting isn't mysterious "
                 "art. It's clear communication with a literal colleague.",
        "verifiers": [
            "I know how to give the AI a role in a prompt.",
            "I know how to specify the exact output format.",
            "I know how to use negative constraints.",
        ],
        "build_this": "Pick a real task from your work. Write 3 prompt "
                      "versions: bad, with role, with example. Test them "
                      "in a chat AI. Keep the one that works.",
        "method_name": "3-prompt test",
        "method_summary": "Pick a real task from work. Write 3 variants: bad "
                          "(no context), with role (who the AI is), with "
                          "example (show what you want). Test them.",
        "method_when": "When your prompt gives weak results and you don't know why.",
    },
    "ch4": {
        "title": "Vision and multimodal AI",
        "subtitle": "Classification, detection, OCR, segmentation. The second-largest AI category by economic impact.",
        "intro": "Computer Vision (CV) is the AI category that works with "
                 "images and video: recognizes objects, reads text, tracks "
                 "motion, generates new images. Second only to LLMs in economic impact.",
        "verifiers": [
            "I know the difference between classification, detection, and segmentation.",
            "I can use a hosted vision API to label an image in under 5 minutes.",
            "I can describe when to use a cloud vision API vs. a local model.",
        ],
        "build_this": "Download 20 photos of cats and 20 of dogs. Upload "
                      "them to Google Cloud Vision (or Roboflow free "
                      "tier). Compare the labels to your own.",
        "method_name": "20 photos, 1 tool",
        "method_summary": "Take 20 personal photos (cats, food, documents). "
                          "Upload them to Google Cloud Vision. Compare "
                          "the AI labels to what you know is in the image.",
        "method_when": "When you need to label, crop, or extract text from images at scale.",
    },
    "ch5": {
        "title": "Text, writing, and summarization",
        "subtitle": "Where LLMs actually win day-to-day: drafting, summarizing, rewriting, translating.",
        "intro": "Image and video generation is impressive, but the "
                 "everyday LLM win is text: drafting, summarizing, "
                 "rewriting, and translating — the work your team does "
                 "every day, made 3–5× faster.",
        "verifiers": [
            "I can write a prompt that produces a consistent tone over 10 outputs.",
            "I can summarize a 5-page document into a one-paragraph brief.",
            "I can rewrite a paragraph in 3 different registers (formal, casual, technical).",
        ],
        "build_this": "Pick a long document you wrote this month (a "
                      "report, an email thread, a doc). Write 3 prompts: "
                      "summarize in 3 sentences, extract action items, "
                      "rewrite for a different audience.",
        "method_name": "One doc, three prompts",
        "method_summary": "Take any long text. Write 3 prompts: summarize "
                          "in 3 sentences, extract action items, rewrite "
                          "for a different audience. Compare to your own "
                          "first attempt.",
        "method_when": "When you have a long text to process and want a quick, reusable approach.",
    },
    "ch6": {
        "title": "AI tools and workflows",
        "subtitle": "Coding assistants, research tools, image tools, productivity agents. Choose by job, not by hype.",
        "intro": "There are now thousands of AI tools. The trap is "
                 "collecting them. The skill is picking the right one for "
                 "the job — coding, research, image, or workflow — and "
                 "sticking with it long enough to learn its quirks.",
        "verifiers": [
            "I can name one tool per category (coding / research / image / agents) and what it's good at.",
            "I have a default AI coding assistant set up with project memory.",
            "I can write a workflow spec for a small agent (input, check, failure path).",
        ],
        "build_this": "Pick one task you do every week. Find the AI tool "
                      "that category recommends. Use it for two weeks "
                      "before judging. Write 3 lines: what worked, what "
                      "didn't, what you'd try next.",
        "method_name": "Two-week tool trial",
        "method_summary": "Pick one weekly task, pick the recommended tool "
                          "for that category, use it for two weeks before "
                          "forming an opinion. Write a 3-line retro: what "
                          "worked, what didn't, what's next.",
        "method_when": "When a new AI tool launches and you're tempted to switch on day one.",
    },
    "ch7": {
        "title": "Embeddings and RAG basics",
        "subtitle": "How to give the AI context from your own data. Vector DB + retrieval.",
        "intro": "LLMs know a lot, but they know nothing specific about you "
                 "or your company. That's a fundamental limit. The solution: "
                 "RAG (Retrieval-Augmented Generation) — add context from "
                 "your own documents before the model answers.",
        "verifiers": [
            "I know what an embedding is and how similarity is computed.",
            "I can stand up a small vector DB (Chroma or similar) on my own files.",
            "I can read a citation and tell if the cited chunk actually supports the answer.",
        ],
        "build_this": "Take 10 of your own documents (articles, wiki "
                      "pages, notes). Load them into Chroma (local, free). "
                      "Ask 5 questions. Verify: did the cited chunk actually "
                      "support the answer?",
        "method_name": "10 docs, 1 question",
        "method_summary": "Take 10 of your own files. Load into Chroma. "
                          "Ask 5 questions. For each, check the cited "
                          "chunk — most RAG bugs are silent, not loud.",
        "method_when": "When you're tempted to fine-tune. Try RAG first; it's 10× cheaper and faster.",
    },
    "ch8": {
        "title": "Agents and automation",
        "subtitle": "LLM + tools + loop. From chat to automation. MCP as USB-C for AI.",
        "intro": "An LLM alone answers questions. An agent makes decisions, "
                 "calls tools, and iterates. The difference is between a "
                 "calculator and an operator.",
        "verifiers": [
            "I know what an agent is and how it differs from a simple tool call.",
            "I can write (tool, input, check, failure path) tuples for a real task.",
            "I can spot a workflow that has no recovery path and call it out.",
        ],
        "build_this": "Use Claude Code or Cursor on a small project. Give "
                      "it a simple task: \"add tests for function X\". "
                      "Watch how it plans, calls tools, and recovers from "
                      "failures. Take notes.",
        "method_name": "Agent on a small project",
        "method_summary": "Use Claude Code or Cursor on a small project "
                          "(100–200 lines). Give it one task. Watch the "
                          "trace: which tools it called, which calls failed, "
                          "how it recovered. Take notes.",
        "method_when": "When you have a multi-step task that always comes back the next week.",
    },
    "ch9": {
        "title": "Evaluation and trust",
        "subtitle": "How do you know the AI is right? Eval is the difference between a demo and a product.",
        "intro": "Chat = for you. SDK = for your program. Ollama = local. "
                 "OpenRouter = 50+ models. But none of that matters if you "
                 "can't tell when the model is wrong.",
        "verifiers": [
            "I can define a 5-example test set for any task I care about.",
            "I can spot the difference between a vibe check and an eval set.",
            "I know when to trust a model and when to keep a human in the loop.",
        ],
        "build_this": "Pick a task you do weekly. Write 5 example "
                      "input/output pairs. Save them as your eval set. "
                      "Run any new model or prompt through them before "
                      "shipping it. Score pass / fail.",
        "method_name": "5-input eval set",
        "method_summary": "Pick a weekly task. Write 5 example input/output "
                          "pairs. Run any new model or prompt through them "
                          "before shipping. Score pass / fail. Re-run when "
                          "anything changes.",
        "method_when": "Before you ship any AI feature that ships to a real user.",
    },
    "ch10": {
        "title": "Building your own AI workflow",
        "subtitle": "You have the projects. Apply to 3 roles today. We are all in this.",
        "intro": "You learned. Now you have to earn. The difference between "
                 "\"I know AI\" and \"I have the projects\" is the salary. "
                 "Pick three roles you could apply to today and apply.",
        "verifiers": [
            "I have picked a target role (AI engineer / ML engineer / MLOps / etc.).",
            "I have one project I can show in 2 minutes.",
            "I can describe in one sentence why my last project is interesting.",
        ],
        "build_this": "Pick 3 job listings on LinkedIn for your target role. "
                      "Apply to one NOW. The other two tomorrow morning. "
                      "Save the link to each application so you can follow up.",
        "method_name": "Apply today",
        "method_summary": "Pick 3 LinkedIn listings. Apply to one right now. "
                          "The other two tomorrow morning. Save the link to "
                          "each so you can follow up next week.",
        "method_when": "Right now. Don't wait until you feel ready.",
    },
}
# Each Today pick: (label, title, body, target_section, action_label).
# target_section is the internal DISPATCH key the button routes to.
_TODAY_PICKS = [
    ("Tool of the day",
     "Cursor rules / project memory",
     "Drop your team's coding standards into a small rules file the assistant reads on every request. Less repetition, fewer style debates.",
     "news", "Open Tools"),
    ("Prompt kit to try",
     "Ship a feature safely",
     "Before any code, force four lists: files to touch, risks, tests, and a one-line rollback. Cheap to run, catches most preventable rollbacks.",
     "prompts", "Open Prompt Kits"),
    ("Skill to learn",
     "RAG evaluation basics",
     "Most RAG bugs are silent — the answer looks right but the citation is missing. Learn the four checks that catch them before users do.",
     "learning", "Open Learn"),
    ("Career signal",
     "AI product operator",
     "Teams need people who turn a model into a workflow a real team uses weekly. It's the role hiring managers keep asking about, with no clear default candidate.",
     "jobs", "Open Jobs"),
]


_STATIC_CSS = """<style>
/* PR15 chrome cleanup — global suppressors. */
div.or-radar, div.or-scan { display: none !important; }
div.or-nav-pills {
  background: transparent !important;
  border: 0 !important;
  padding: 0 !important;
}
.or-hero .or-eyebrow::before,
.or-hero .or-eyebrow::after { display: none !important; }
.or-hero { padding: 0 !important; min-height: 0 !important; }
.or-hero h1 {
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif !important;
  font-weight: 700 !important;
  letter-spacing: -0.02em !important;
}

/* PR16 header brand + nav cleanup — keep header as a compact workbench
   bar. Brand wordmark + one-line subtitle stay readable on desktop,
   refresh action is quiet, nav buttons sit on a single row. */
section.main > div { padding-top: 0.35rem !important; }

.or-topnav-brand {
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  line-height: 1 !important;
}
.or-topnav-brand .or-name {
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif !important;
  font-size: 1.05rem !important;
  font-weight: 700 !important;
  letter-spacing: -0.02em !important;
  color: var(--text) !important;
  line-height: 1 !important;
  white-space: nowrap !important;
}
.or-topnav-brand .or-name-stack {
  display: inline-flex !important;
  flex-direction: column !important;
  gap: 0.18rem !important;
  line-height: 1 !important;
}
.or-topnav-brand .or-name-kicker {
  font-family: 'JetBrains Mono', 'SF Mono', Menlo, monospace !important;
  font-size: 0.52rem !important;
  font-weight: 600 !important;
  letter-spacing: 0.06em !important;
  text-transform: none !important;
  color: var(--muted-2) !important;
  line-height: 1 !important;
  white-space: nowrap !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
  max-width: 100% !important;
}
.or-topnav-brand .or-mark { display: none !important; }

/* Nav shell — no decorative frame, single row, even gaps. */
div.or-nav-shell {
  display: flex !important;
  gap: 0.25rem !important;
  align-items: center !important;
  justify-content: flex-start !important;
  padding: 0 !important;
  margin: 0 !important;
  background: transparent !important;
  border: 0 !important;
}
[class*="st-key-nav_"] button {
  white-space: nowrap !important;
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif !important;
  font-size: 0.8rem !important;
  font-weight: 600 !important;
  letter-spacing: -0.005em !important;
  text-transform: none !important;
  border-radius: 8px !important;
  padding: 0.4rem 0.6rem !important;
  min-height: 30px !important;
  height: 30px !important;
  line-height: 1 !important;
  box-shadow: none !important;
  transition: none !important;
}
[class*="st-key-nav_"] button[data-testid="stBaseButton-primary"],
[class*="st-key-nav_"] button[data-testid="baseButton-primary"] {
  background: rgba(214, 154, 95, 0.18) !important;
  color: #fff7ed !important;
  border: 1px solid rgba(214, 154, 95, 0.55) !important;
  font-weight: 700 !important;
}
[class*="st-key-nav_"] button[data-testid="stBaseButton-secondary"],
[class*="st-key-nav_"] button[data-testid="baseButton-secondary"] {
  background: transparent !important;
  color: var(--muted) !important;
  border: 1px solid transparent !important;
  font-weight: 600 !important;
}
[class*="st-key-nav_"] button[data-testid="stBaseButton-secondary"]:hover,
[class*="st-key-nav_"] button[data-testid="baseButton-secondary"]:hover {
  background: rgba(255, 255, 255, 0.03) !important;
  color: var(--text) !important;
  border-color: rgba(148, 163, 184, 0.22) !important;
}

/* Quiet refresh action — text button, no chrome, small footprint. */
.st-key-nav_refresh button,
[data-testid="stColumn"]:has(.st-key-nav_refresh) button {
  background: transparent !important;
  color: var(--muted) !important;
  border: 1px solid rgba(148, 163, 184, 0.22) !important;
  border-radius: 8px !important;
  padding: 0.3rem 0.55rem !important;
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif !important;
  font-size: 0.74rem !important;
  font-weight: 600 !important;
  letter-spacing: -0.005em !important;
  text-transform: none !important;
  min-height: 30px !important;
  height: 30px !important;
  line-height: 1 !important;
}
[data-testid="stColumn"]:has(.st-key-nav_refresh) button:hover {
  background: rgba(255, 255, 255, 0.03) !important;
  color: var(--text) !important;
  border-color: rgba(148, 163, 184, 0.32) !important;
}

section.or-workbench-hero {
  margin: 0.15rem 0 0.55rem 0;
  padding: 0;
}
section.or-workbench-hero h1 {
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  font-size: clamp(1.35rem, 2.2vw, 1.7rem);
  font-weight: 750;
  letter-spacing: -0.02em;
  line-height: 1.15;
  margin: 0 0 0.25rem 0;
  color: var(--text);
}
section.or-workbench-hero p {
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  font-size: 0.9rem;
  line-height: 1.4;
  color: var(--text-2);
  margin: 0;
  max-width: 720px;
}

div.or-static-action .or-static-label {
  font-family: 'JetBrains Mono', 'SF Mono', Menlo, monospace;
  font-size: 0.6rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--muted);
  display: block;
  margin: 0 0 0.3rem 0;
}
div.or-static-action .or-static-title {
  font-size: 0.98rem;
  font-weight: 600;
  color: var(--text);
  display: block;
  margin: 0 0 0.3rem 0;
  line-height: 1.25;
}
div.or-static-action .or-static-body {
  font-size: 0.82rem;
  color: var(--text-2);
  line-height: 1.4;
  margin: 0 0 0.6rem 0;
}

/* PR19 · Learn guided-course chrome — scoped to or-learn-* classes. */
section.or-learn-hero {
  margin: 0.4rem 0 0.8rem 0;
  padding: 0;
}
section.or-learn-hero h1 {
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  font-size: clamp(1.5rem, 2.6vw, 2.05rem);
  font-weight: 750;
  letter-spacing: -0.02em;
  line-height: 1.12;
  margin: 0.2rem 0 0.45rem 0;
  color: var(--text);
}
section.or-learn-hero p {
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  font-size: 0.92rem;
  line-height: 1.45;
  color: var(--text-2);
  margin: 0;
  max-width: 720px;
}
.or-learn-eyebrow {
  font-family: 'JetBrains Mono', 'SF Mono', Menlo, monospace;
  font-size: 0.6rem;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--muted);
  margin: 0 0 0.35rem 0;
}
.or-learn-progress-num {
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  font-size: 0.78rem;
  color: var(--text-2);
  white-space: nowrap;
}
.or-learn-progress-num strong {
  font-size: 1.05rem;
  font-weight: 700;
  color: var(--text);
  margin-right: 0.15rem;
}
.or-learn-progress-num span {
  color: var(--muted);
  font-size: 0.72rem;
}
@media (max-width: 720px) {
  /* On narrow screens, stack the progress number above the bar. */
  .or-learn-progress-num { margin-bottom: 0.3rem; }
}

/* PR19 · Mobile layout — scoped overrides, no desktop regression.
   - <920px : Learn two columns collapse to single column.
   - <720px : Learn hero shorter, path cards 2-up, chapter nav shorter,
              prev/next/toggle stack vertically, hero/title smaller.
   - <560px : Tighter padding, smaller chapter numerals. */
@media (max-width: 920px) {
  /* Two-column guide -> single column. Chapter list on top so users
     see the path of chapters before the reading panel. */
  [data-testid="stHorizontalBlock"]:has(.or-learn-guide) {
    flex-wrap: wrap !important;
  }
  [data-testid="stHorizontalBlock"]:has(.or-learn-guide) > [data-testid="stColumn"] {
    flex: 1 0 100% !important;
    max-width: 100% !important;
    min-width: 100% !important;
  }
  /* Path quick-links (4-up) -> 2-up on tablet. */
  [data-testid="stHorizontalBlock"]:has(.or-static-action) {
    flex-wrap: wrap !important;
  }
  [data-testid="stHorizontalBlock"]:has(.or-static-action) > [data-testid="stColumn"] {
    flex: 1 0 calc(50% - 0.25rem) !important;
    max-width: calc(50% - 0.25rem) !important;
  }
  /* Bottom nav (Previous / Mark complete / Next) -> 3-up stays 3-up
     on tablet — buttons are short enough. */
}
@media (max-width: 720px) {
  /* Learn hero: shorter on mobile. */
  section.or-learn-hero { margin: 0.2rem 0 0.55rem 0; }
  section.or-learn-hero h1 {
    font-size: clamp(1.2rem, 5.2vw, 1.65rem);
    margin: 0.1rem 0 0.3rem 0;
  }
  section.or-learn-hero p { font-size: 0.86rem; line-height: 1.4; }
  /* Path quick-links: keep 2-up. */
  [data-testid="stHorizontalBlock"]:has(.or-static-action) > [data-testid="stColumn"] {
    flex: 1 0 calc(50% - 0.25rem) !important;
    max-width: calc(50% - 0.25rem) !important;
  }
  /* Chapter nav: tighter button labels on small screens. The button
     labels include the chapter number + title which can be long; rely
     on Streamlit's default text-wrap and let the button grow. */
  [data-testid="stHorizontalBlock"]:has(.or-learn-chapter-list) > [data-testid="stColumn"] {
    flex: 1 0 100% !important;
    max-width: 100% !important;
    min-width: 100% !important;
  }
  /* Bottom nav (Previous / Mark complete / Next) -> stack vertically. */
  [data-testid="stHorizontalBlock"]:has(.or-learn-bottom-nav) {
    flex-direction: column !important;
    gap: 0.4rem !important;
  }
  [data-testid="stHorizontalBlock"]:has(.or-learn-bottom-nav) > [data-testid="stColumn"] {
    flex: 1 0 100% !important;
    max-width: 100% !important;
    min-width: 100% !important;
  }
  /* Top nav: hide the narrow refresh column on mobile (the nav is the
     primary navigation; refresh is a dev affordance, not a user one).
     Brand keeps its single column; nav buttons get a full row. */
  [data-testid="stHorizontalBlock"]:has(.st-key-nav_refresh) {
    display: none !important;
  }
  /* Make the brand + nav columns stack as full-width rows. */
  [data-testid="stHorizontalBlock"]:has(.or-topnav-brand) {
    flex-wrap: wrap !important;
    row-gap: 0.55rem !important;
  }
  [data-testid="stHorizontalBlock"]:has(.or-topnav-brand) > [data-testid="stColumn"] {
    flex: 1 0 100% !important;
    max-width: 100% !important;
    min-width: 100% !important;
  }
  /* Nav buttons: full width on mobile. */
  [data-testid="stHorizontalBlock"]:has(.or-nav-shell) > [data-testid="stColumn"] {
    flex: 1 0 100% !important;
    max-width: 100% !important;
    min-width: 100% !important;
  }
  /* Hide the brand subtitle on mobile — keep just "OpenRadar" so the
     brand line is single-line and not cramped. */
  .or-topnav-brand .or-name-kicker { display: none !important; }
  /* The workbench hero (Home) also shortens on mobile. */
  section.or-workbench-hero { margin: 0.1rem 0 0.4rem 0; }
  section.or-workbench-hero h1 { font-size: clamp(1.2rem, 5.5vw, 1.7rem); }
  section.or-workbench-hero p { font-size: 0.86rem; }
}
@media (max-width: 560px) {
  /* Tighter padding on very small screens. */
  section.main > div { padding-top: 0.25rem !important; }
  section.or-learn-hero { margin: 0.1rem 0 0.4rem 0; }
  /* Chapter numeral — slightly smaller. */
  .lrn-numeral { font-size: 3.5rem !important; }
  /* All action card text a touch smaller. */
  div.or-static-action .or-static-title { font-size: 0.9rem !important; }
  div.or-static-action .or-static-body { font-size: 0.78rem !important; }
}
</style>"""


def _read_focus(state_key: str) -> str | None:
    """Read the selected card key from query_params or session_state."""
    qp_val = st.query_params.get(state_key)
    if qp_val:
        st.session_state[state_key] = qp_val
        return qp_val
    return st.session_state.get(state_key)


def _render_action_cards(items: list, state_key: str, action_label: str = "Open") -> None:
    """Render a 4-up row of Streamlit-native action cards.

    Each card has separated label/title/body + an `st.button` that sets
    `st.session_state[state_key]` and `?state_key=...` to the card's key,
    then reruns so the selected detail panel updates immediately.

    Cards in `_STATIC_LEARN` carry an extra `chapter` field (a chapter
    id string). When a Learn path-card is clicked, the card also sets
    `st.session_state["selected_chapter"]` so the guided Learn view
    jumps to that chapter.
    """
    st.markdown(_STATIC_CSS, unsafe_allow_html=True)
    cols = st.columns(len(items), gap="small")
    for col, item in zip(cols, items):
        # Item shape is either 5-tuple (key, label, title, body, detail)
        # or 6-tuple (key, label, title, body, chapter_id, detail).
        if len(item) == 6:
            key, label, title, body, chapter_id, _detail = item
        else:
            key, label, title, body, _detail = item
            chapter_id = None
        with col:
            with st.container(border=True):
                st.markdown(
                    f"<div class='or-static-action'><div class='or-static-label'>"
                    f"{esc(label)}</div>"
                    f"<div class='or-static-title'>{esc(title)}</div>"
                    f"<p class='or-static-body'>{esc(body)}</p></div>",
                    unsafe_allow_html=True,
                )
                if st.button(
                    action_label,
                    key=f"{state_key}_open_{key}",
                    use_container_width=True,
                    type="primary",
                ):
                    st.session_state[state_key] = key
                    st.query_params[state_key] = key
                    if chapter_id:
                        st.session_state["selected_chapter"] = chapter_id
                        st.query_params["learn_chapter"] = chapter_id
                    st.rerun()


def _render_selected_detail(items: list, state_key: str, panel_heading: str) -> None:
    """Render the selected card's detail panel below the card row.

    If nothing is selected, render a small "select a card" prompt. The
    panel uses Streamlit-native widgets so label / body / checklist /
    next-action are always rendered as separate elements.
    """
    selected_key = _read_focus(state_key)
    if not selected_key:
        st.markdown(
            "<div style='font-family:\"JetBrains Mono\",\"SF Mono\",Menlo,monospace;"
            "font-size:0.65rem;letter-spacing:0.12em;text-transform:uppercase;"
            "color:var(--muted);margin:0.4rem 0 0.2rem 0;'>"
            "SELECTED · pick a card above to see the detail</div>",
            unsafe_allow_html=True,
        )
        return

    match = next((item for item in items if item[0] == selected_key), None)
    if match is None:
        # Stale key from a previous session — clear it and re-prompt.
        st.session_state.pop(state_key, None)
        st.query_params.pop(state_key, None)
        st.rerun()
        return

    # _STATIC_LEARN items are 6-tuples (key, label, title, body, chapter_id,
    # detail); all other section items are 5-tuples (key, label, title, body,
    # detail). Take the first 5 fields explicitly so both shapes unpack
    # cleanly and the detail dict always lives in slot 5.
    key, label, title, body, detail = match[0], match[1], match[2], match[3], match[5] if len(match) > 5 else match[4]
    with st.container(border=True):
        st.markdown(
            f"<div style='font-family:\"JetBrains Mono\",\"SF Mono\",Menlo,monospace;"
            f"font-size:0.6rem;letter-spacing:0.12em;text-transform:uppercase;"
            f"color:var(--amber);margin-bottom:0.25rem;'>{esc(panel_heading)} · "
            f"{esc(label)}</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<div style='font-size:1.05rem;font-weight:700;color:var(--text);"
            f"margin-bottom:0.5rem;line-height:1.2;'>{esc(title)}</div>",
            unsafe_allow_html=True,
        )
        # Per-section detail fields — pick keys that exist in this item's detail.
        if "what" in detail:
            st.markdown("**What it helps with**")
            st.markdown(detail["what"])
        if "best_for" in detail:
            st.markdown("**Best for**")
            st.markdown(detail["best_for"])
        if "use_case" in detail:
            st.markdown("**Use case**")
            st.markdown(detail["use_case"])
        if "understand" in detail:
            st.markdown("**What you will understand**")
            st.markdown(detail["understand"])
        if "why" in detail:
            st.markdown("**Why it matters**")
            st.markdown(detail["why"])
        if "does" in detail:
            st.markdown("**What the role does**")
            st.markdown(detail["does"])
        if "when" in detail:
            st.markdown("**When to use**")
            st.markdown(detail["when"])
        if "when_not" in detail:
            st.markdown("**When not to use**")
            st.markdown(detail["when_not"])
        if "inputs" in detail:
            st.markdown("**Inputs to gather**")
            st.markdown(detail["inputs"])
        if "starter" in detail:
            st.markdown("**Starter prompt**")
            st.markdown(
                "<div style='font-family:\"JetBrains Mono\",\"SF Mono\",Menlo,monospace;"
                "font-size:0.78rem;color:var(--text-2);background:var(--surface);"
                "padding:0.55rem 0.7rem;border-radius:8px;border:1px solid var(--border);"
                "margin:0.25rem 0 0.5rem 0;'>" + esc(detail["starter"]) + "</div>",
                unsafe_allow_html=True,
            )
        if "quality" in detail:
            st.markdown("**Quality check**")
            st.markdown(detail["quality"])
        if "checklist" in detail:
            st.markdown("**Starter checklist**")
            for step in detail["checklist"]:
                st.markdown(f"- {esc(step)}")
        if "compare" in detail:
            st.markdown("**What to compare before choosing**")
            st.markdown(detail["compare"])
        if "exercise" in detail:
            st.markdown("**One practical exercise**")
            st.markdown(detail["exercise"])
        if "mistake" in detail:
            st.markdown("**Common mistake**")
            st.markdown(detail["mistake"])
        if "skills" in detail:
            st.markdown("**Skills to learn**")
            for s in detail["skills"]:
                st.markdown(f"- {esc(s)}")
        if "proof" in detail:
            st.markdown("**Portfolio proof idea**")
            st.markdown(detail["proof"])
        if "next_chapter" in detail:
            st.markdown(f"**Recommended next chapter** — {esc(detail['next_chapter'])}")
        if "next" in detail:
            st.markdown("**Next action**")
            st.markdown(detail["next"])
        if "search_terms" in detail:
            st.markdown("**Search terms**")
            st.markdown(", ".join(f"`{esc(t)}`" for t in detail["search_terms"]))
        if "warning" in detail:
            st.markdown("**Watch out**")
            st.markdown(detail["warning"])
        if "related" in detail:
            st.markdown(
                f"<div style='font-family:\"JetBrains Mono\",\"SF Mono\",Menlo,monospace;"
                f"font-size:0.62rem;color:var(--muted);margin-top:0.5rem;'>"
                f"{esc(detail['related'])}</div>",
                unsafe_allow_html=True,
            )
        if st.button(
            "Clear selection",
            key=f"{state_key}_clear",
            use_container_width=False,
        ):
            st.session_state.pop(state_key, None)
            st.query_params.pop(state_key, None)
            st.rerun()


def _render_english_chapter(selected_id: str, ch_list: list, completed: set) -> None:
    """PR19 English surface layer for the Learn guide.

    Wraps the existing rich lecture content (Romanian body, verifiers,
    methods, cross-refs) with English surface labels. The Romanian
    body_md is NOT rendered — a "Looking for more?" placeholder sits
    in its place so the page rhythm is preserved. Falls back gracefully
    to the original renderer if no English localization is available.
    """
    from learning.learning_render import render_detail_panel
    ch = next((c for c in ch_list if c.id == selected_id), None)
    if ch is None:
        return
    loc = _LOCALIZE.get(ch.id)
    if not loc:
        # No localization for this chapter — fall back to the rich
        # renderer so we never lose content.
        render_detail_panel(selected_id, ch_list, completed)
        return

    # ── English header (numeral / title / subtitle) ────────────────
    accent = domain_color(ch.domain)
    idx = next((i for i, c in enumerate(ch_list) if c.id == ch.id), 0)
    st.markdown(
        '<div class="lrn-breadcrumb">❡ Learn · Chapter</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="lrn-numeral" style="color:{accent};">{ch.number:02d}</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="lrn-domain-tag" style="color:{accent};">'
        f'{esc(ch.domain)}'
        f'&nbsp;&nbsp;<span style="color:#6a6458;">era {esc(ch.era)}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<h1 class="lrn-title">{esc(loc["title"])}</h1>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<p class="lrn-subtitle">{esc(loc["subtitle"])}</p>',
        unsafe_allow_html=True,
    )

    # ── English intro paragraph (visible chapter intro text) ─────
    st.markdown(
        f'<div class="lrn-body">{esc(loc["intro"])}</div>',
        unsafe_allow_html=True,
    )

    # ── English checklist (Build this) ───────────────────────────
    st.markdown(
        f'<div class="lrn-domain-tag" style="color:{accent};">'
        f'▸ Build this (20 minutes)</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="lrn-body">{esc(loc["build_this"])}</div>',
        unsafe_allow_html=True,
    )

    # ── English verifiers (auto-complete when all ticked) ─────────
    if loc.get("verifiers"):
        st.markdown(
            f'<div class="lrn-domain-tag" style="color:{accent};">'
            f'✓ Self-check (tick all to mark complete)</div>',
            unsafe_allow_html=True,
        )
        all_ticked = True
        for vi, v in enumerate(loc["verifiers"]):
            key = f"verifier_{ch.id}_{vi}"
            ticked = bool(st.session_state.get(key, False))
            if not ticked:
                all_ticked = False
            st.checkbox(v, key=key)

        if all_ticked:
            if ch.id not in completed:
                completed = set(completed) | {ch.id}
                st.session_state.completed_chapters = completed
            st.markdown(
                '<div class="lrn-completion">'
                '<div class="lrn-completion-msg">'
                'All checks ticked — this chapter is done.'
                '</div>'
                '<div class="lrn-completion-sub">'
                'self-check complete · chapter complete'
                '</div>'
                '</div>',
                unsafe_allow_html=True,
            )

    # ── English recommended method ──────────────────────────────
    if loc.get("method_name"):
        st.markdown('<hr class="lrn-rule" />', unsafe_allow_html=True)
        st.markdown(
            f'<div class="lrn-domain-tag" style="color:{accent};">'
            f'◆ Recommended method</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="lrn-method">'
            f'<div class="lrn-method-name">{esc(loc["method_name"])}</div>'
            f'<div class="lrn-method-summary">{esc(loc["method_summary"])}</div>'
            f'<div class="lrn-method-why">'
            f'When to use: {esc(loc["method_when"])}'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
        st.checkbox(
            f"I tried \"{loc['method_name']}\"",
            key=f"method_done_{ch.id}_main",
        )

    # ── Detailed notes section ─────────────────────────────────────
    # Original Romanian body_md intentionally not rendered in
    # English-first guide until full translation lands. The source
    # content stays in `learning/learning_render._render_body_md` and
    # `content/chapters.jsonl` for future translation work; we just
    # skip emitting it here so the visible Learn UI is 100% English.
    # A short "Looking for more?" placeholder keeps the page rhythm
    # honest without reintroducing the Romanian copy.
    st.markdown('<hr class="lrn-rule" />', unsafe_allow_html=True)
    st.markdown(
        f'<div class="lrn-domain-tag" style="color:{accent};">'
        f'▸ Looking for more?</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="lrn-body" style="color: var(--text-2); '
        'font-size: 0.9rem;">'
        'Detailed chapter notes are still being translated from the '
        'original Romanian drafts. The structure above (intro, '
        'self-check, recommended method, cross-references) covers '
        'the core of every chapter.'
        '</div>',
        unsafe_allow_html=True,
    )

    # ── Cross-refs (NEWS / TOOL / PROMPT links from the loader) ───
    import html as _html
    try:
        from learning.learning_render import _load_cross_refs
        cr = _load_cross_refs(ch.id)
        has_any = cr["news"] or cr["repos"] or cr["prompts"]
        if has_any:
            st.markdown('<hr class="lrn-rule" />', unsafe_allow_html=True)
            st.markdown(
                f'<div class="lrn-domain-tag" style="color:{accent};">'
                f'▸ From our feed</div>',
                unsafe_allow_html=True,
            )
            for n in cr["news"]:
                st.markdown(
                    f'<div style="margin: 0.4rem 0; font-size: 0.95rem;">'
                    f'<span class="lrn-footer" style="margin-right: 0.5rem;">NEWS</span>'
                    f'<a href="{_html.escape(n["url"])}" target="_blank" '
                    f'style="color: #f4ede0; text-decoration: none; '
                    f'border-bottom: 1px dashed #3a342c;">'
                    f'{_html.escape(n["title"][:90])}</a></div>',
                    unsafe_allow_html=True,
                )
            for r in cr["repos"]:
                st.markdown(
                    f'<div style="margin: 0.4rem 0; font-size: 0.95rem;">'
                    f'<span class="lrn-footer" style="margin-right: 0.5rem;">TOOL</span>'
                    f'<a href="{_html.escape(r["url"])}" target="_blank" '
                    f'style="color: #f4ede0; text-decoration: none; '
                    f'border-bottom: 1px dashed #3a342c;">'
                    f'{_html.escape(r["title"])}</a></div>',
                    unsafe_allow_html=True,
                )
            for p in cr["prompts"]:
                cat = (p.get("category") or "?").upper()
                diff = (p.get("difficulty") or "?").upper()
                st.markdown(
                    f'<div style="margin: 0.4rem 0; font-size: 0.95rem;">'
                    f'<span class="lrn-footer" style="margin-right: 0.5rem;">'
                    f'PROMPT · {cat} · {diff}</span>'
                    f'<span style="color: #f4ede0;">'
                    f'{_html.escape(p["title"][:90])}</span></div>',
                    unsafe_allow_html=True,
                )
    except Exception:
        # Cross-refs are best-effort. If the loader raises, skip them.
        pass

    # ── Footer progress strip ─────────────────────────────────────
    total = len(ch_list)
    done = sum(1 for c in ch_list if c.id in completed)
    pct = int(done / total * 100) if total else 0
    next_ch = ch_list[idx + 1] if idx < total - 1 else None
    next_label = (
        f"{next_ch.number:02d} · {next_ch.title}"
        if next_ch else "last chapter"
    )
    st.markdown('<hr class="lrn-rule" />', unsafe_allow_html=True)
    st.markdown(
        f'<div class="lrn-footer">'
        f'{ch.number:02d} / {total:02d}&nbsp;&nbsp;·&nbsp;&nbsp;'
        f'{pct}% complete&nbsp;&nbsp;·&nbsp;&nbsp;'
        f'next: {_html.escape(next_label)}'
        f'</div>',
        unsafe_allow_html=True,
    )


def _render_today_picks() -> None:
    cols = st.columns(4, gap="small")
    for col, pick in zip(cols, _TODAY_PICKS):
        label, title, body, target, action = pick
        with col:
            with st.container(border=True):
                st.markdown(
                    f"<div style='font-family:\"JetBrains Mono\",\"SF Mono\",Menlo,monospace;"
                    f"font-size:0.6rem;letter-spacing:0.12em;text-transform:uppercase;"
                    f"color:var(--muted);'>{esc(label)}</div>",
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f"<div style='font-size:0.98rem;font-weight:600;color:var(--text);"
                    f"margin:0.25rem 0 0.4rem 0;line-height:1.25;'>{esc(title)}</div>",
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f"<p style='font-size:0.82rem;color:var(--text-2);"
                    f"line-height:1.4;margin:0 0 0.6rem 0;'>{esc(body)}</p>",
                    unsafe_allow_html=True,
                )
                if st.button(
                    action,
                    key=f"today_open_{target}",
                    use_container_width=True,
                    type="primary",
                ):
                    st.session_state.section = target
                    st.query_params["section"] = target
                    st.rerun()


def render_groq() -> None:
    """The default landing: compact workbench hero, then the Today picks row,
    then the existing live bento of News / Tools / Jobs."""

    # PR15 chrome cleanup: inject the workbench CSS (global suppressors +
    # .or-workbench-hero style) early so the chrome applies on Home even
    # when no action card row is rendered.
    st.markdown(_STATIC_CSS, unsafe_allow_html=True)

    # PR15 chrome cleanup: compact workbench hero instead of the old
    # cinematic serif hero. Modern system sans, no eyebrow line, no fake
    # status pill. The .or-workbench-hero class is the single source of
    # truth for the new hero styling — it overrides .or-hero below in
    # theme.py.
    st.markdown(
        '<section class="or-workbench-hero">'
        '<h1>Your AI workbench for tools, prompts, learning, and jobs.</h1>'
        '<p>Find useful AI tools, reusable prompt kits, practical '
        'learning paths, and career signals without drowning in noise.</p>'
        '</section>',
        unsafe_allow_html=True,
    )

    # PR15: explicit Today picks — small static module, no glued text.
    section_head(
        "TODAY · STATIC PICKS",
        "Today",
        "Four practical picks for today’s workbench session.",
    )
    _render_today_picks()

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
        "TOOLS · STATIC WORKBENCH CATEGORIES",
        "Tools",
        "Four practical categories of AI tools — pick the one that matches the job.",
    )
    _render_action_cards(_STATIC_TOOLS, state_key="tools_focus", action_label="Open")
    _render_selected_detail(_STATIC_TOOLS, state_key="tools_focus",
                            panel_heading="SELECTED TOOL CATEGORY")
    section_head(
        "FEEDS · CURRENT TOOLS RADAR",
        "Live signals",
        "Repos, papers, and discussions worth scanning today.",
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
# PR19: replaces the static-card + selectbox layout with a guided course:
# left column = chapter list with status marks, right column = the
# existing rich lecture renderer (PR-A detail panel from
# learning.learning_render). State stays in session_state + ?learn_chapter=...
# PR1 `_progress` machinery is untouched (it mirrors session_state to ?p=...).
# ─────────────────────────────────────────────────────────────────────────
def render_learning() -> None:
    from learning.learning_render import render_detail_panel
    from theme import lecture_css

    # Header + subheadline (intro line the user sees first).
    st.markdown(
        '<section class="or-learn-hero">'
        '<div class="or-learn-eyebrow">LEARN · GUIDED COURSE</div>'
        '<h1>Learn AI by building useful workflows.</h1>'
        '<p>Pick a path, read one short chapter, do a 20-minute '
        'exercise, mark it complete. No quiz, no certificate — just '
        'practical AI you can actually use at work.</p>'
        '</section>',
        unsafe_allow_html=True,
    )

    # ── Load chapter list ────────────────────────────────────────────
    ch_list = get_all_chapters()
    if not ch_list:
        st.markdown(
            '<div style="padding:1rem;color:var(--muted);">'
            'No chapters available right now. Check '
            '<code>content/chapters.jsonl</code>.'
            '</div>',
            unsafe_allow_html=True,
        )
        return

    chapter_ids = {c.id for c in ch_list}

    # ── Resolve selected chapter from ?learn_chapter= or session_state ──
    qp_chapter = st.query_params.get("learn_chapter")
    if qp_chapter and qp_chapter in chapter_ids:
        st.session_state["selected_chapter"] = qp_chapter

    selected_id = st.session_state.get("selected_chapter")
    if not selected_id or selected_id not in chapter_ids:
        selected_id = ch_list[0].id
        st.session_state["selected_chapter"] = selected_id
        st.query_params["learn_chapter"] = selected_id

    # ── Progress + completed state ──────────────────────────────────
    completed = set(st.session_state.get("completed_chapters", set()) or set())
    done = sum(1 for c in ch_list if c.id in completed)
    total = len(ch_list)
    pct = int(done / total * 100) if total else 0

    progress_cols = st.columns([1, 4])
    with progress_cols[0]:
        st.markdown(
            f'<div class="or-learn-progress-num">'
            f'<strong>{done}</strong>/{total}'
            f'<span>&nbsp;chapters complete</span>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with progress_cols[1]:
        st.progress(min(max(pct, 0), 100))

    # ── Path quick-links: small horizontal strip ────────────────────
    # Each card selects both the path detail panel AND the matching
    # chapter so the user lands in the guide immediately.
    st.markdown(
        '<div class="or-learn-eyebrow" style="margin-top:1rem;">'
        'PICK A PATH</div>',
        unsafe_allow_html=True,
    )
    _render_action_cards(_STATIC_LEARN, state_key="learn_focus",
                         action_label="Start path")

    # ── Two-column guide: chapter list (left) + reading panel (right) ─
    st.markdown('<div class="or-learn-guide">', unsafe_allow_html=True)
    list_col, read_col = st.columns([0.42, 0.58], gap="medium")

    with list_col:
        st.markdown(
            '<div class="or-learn-chapter-list">',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="or-learn-eyebrow" style="margin-top:0.4rem;">'
            'CHAPTERS</div>',
            unsafe_allow_html=True,
        )
        # Each chapter = a button row with status mark + title.
        # Selected chapter gets a visible "current" treatment.
        # Use the English title from _LOCALIZE when available so the
        # chapter list reads in English even though the underlying
        # Chapter.title is Romanian.
        for c in ch_list:
            is_done = c.id in completed
            is_current = c.id == selected_id
            mark = "✓" if is_done else ("•" if is_current else " ")
            display_title = (_LOCALIZE.get(c.id) or {}).get("title") or c.title
            row_label = f"{mark}  {c.number:02d} · {display_title}"
            btn_type = "primary" if is_current else "secondary"
            if st.button(
                row_label,
                key=f"learn_nav_{c.id}",
                use_container_width=True,
                type=btn_type,
            ):
                st.session_state["selected_chapter"] = c.id
                st.query_params["learn_chapter"] = c.id
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)  # close or-learn-chapter-list

    with read_col:
        st.markdown(
            '<div class="or-learn-eyebrow" style="margin-top:0.4rem;">'
            'READING</div>',
            unsafe_allow_html=True,
        )
        st.markdown(lecture_css(), unsafe_allow_html=True)
        # English wrapper around the existing Romanian body. The rich
        # lecture renderer (verifiers / methods / cross-refs / Ask Groq)
        # is the source of truth for content; we re-render the same
        # chapter here with English surface labels and a clear
        # "Detailed notes (Romanian — translation coming)" note for
        # the body copy. Old romanian-only labels are removed in the
        # chapter list and reading header; the rest is preserved.
        _render_english_chapter(selected_id, ch_list, completed)

        # Bottom nav: Previous / Mark complete / Next (clear, explicit).
        idx = next((i for i, c in enumerate(ch_list) if c.id == selected_id), 0)
        prev_ch = ch_list[idx - 1] if idx > 0 else None
        next_ch = ch_list[idx + 1] if idx < total - 1 else None
        st.markdown('<div class="or-learn-bottom-nav">', unsafe_allow_html=True)
        nav_cols = st.columns(3)
        with nav_cols[0]:
            if prev_ch and st.button(
                f"◀ Previous",
                key=f"learn_prev_{selected_id}",
                use_container_width=True,
            ):
                st.session_state["selected_chapter"] = prev_ch.id
                st.query_params["learn_chapter"] = prev_ch.id
                st.rerun()
        with nav_cols[1]:
            is_done = selected_id in completed
            if st.button(
                "Unmark complete" if is_done else "Mark complete ✓",
                key=f"learn_toggle_{selected_id}",
                use_container_width=True,
                type="secondary" if is_done else "primary",
            ):
                if is_done:
                    completed.discard(selected_id)
                else:
                    completed.add(selected_id)
                st.session_state.completed_chapters = set(completed)
                st.rerun()
        with nav_cols[2]:
            if next_ch and st.button(
                f"Next ▶",
                key=f"learn_next_{selected_id}",
                use_container_width=True,
            ):
                st.session_state["selected_chapter"] = next_ch.id
                st.query_params["learn_chapter"] = next_ch.id
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)  # close or-learn-bottom-nav
    st.markdown('</div>', unsafe_allow_html=True)  # close or-learn-guide

    # ── Selected path detail panel (compact, below the two columns) ───
    # Renders the path's static guidance from _STATIC_LEARN. Kept for
    # users who want the high-level "why this path / common mistake /
    # next" view alongside the chapter detail.
    st.markdown(
        '<div class="or-learn-eyebrow" style="margin-top:1.4rem;">'
        'PATH NOTES</div>',
        unsafe_allow_html=True,
    )
    _render_selected_detail(_STATIC_LEARN, state_key="learn_focus",
                            panel_heading="SELECTED PATH")


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
        "JOBS · STATIC ROLE DIRECTIONS",
        "Jobs",
        "Four AI career directions to translate skills into useful work — not a live job board.",
    )
    _render_action_cards(_STATIC_JOBS, state_key="jobs_focus", action_label="Open")
    _render_selected_detail(_STATIC_JOBS, state_key="jobs_focus",
                            panel_heading="SELECTED JOB ROLE")
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
        "PROMPT KITS · STATIC STARTERS",
        "Prompt Kits",
        "Four outcome-grouped prompt starters. Use them to plan, decide, learn, or write.",
    )
    _render_action_cards(_STATIC_PROMPTS, state_key="prompt_focus", action_label="Open")
    _render_selected_detail(_STATIC_PROMPTS, state_key="prompt_focus",
                            panel_heading="SELECTED PROMPT KIT")
    section_head(
        "KITS · BY OUTCOME",
        "Prompt Bible",
        "Colecția completă de prompturi, organizată pe categorii și dificultate.",
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
