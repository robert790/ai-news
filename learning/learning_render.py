"""Learning · detail-panel renderer · OpenRadar v1.0 redesign.

This module owns the entire "what you see when a chapter is open"
experience: header, body markdown render, cross-refs (real links,
no AI generation), Ask Groq Q&A (the ONLY place Groq is used for
Learning), verifiers checkboxes, build-this action, and prev/next
navigation. Right-sidebar meta lives here too.

Why a separate module:
- The Detail Panel used to be ~540 lines of mixed layout/styling/
  data fetch/query logic in app.py. Unreadable.
- Isolating it lets us iterate the visual story without touching
  the rest of the app.
- Imports stay clean: app.py only needs `render_detail_panel()`.

Public API:
    render_detail_panel(selected_id: str,
                        ch_list: list,
                        completed: set) -> None
"""
from __future__ import annotations

import html as _html
from typing import Iterable

import streamlit as st

from learning.chapters import Chapter, get_chapter, domain_color, get_all_chapters
from learning.cross_refs import (
    fetch_quick_news_for_chapter as cr_fetch_news,
    fetch_quick_repos_for_chapter as cr_fetch_repos,
    find_prompts_for_chapter as cr_find_prompts,
)
from learning.insight import ask_groq


# ====================================================================
# Body markdown → HTML
# ====================================================================
#
# Our body markdown is hand-written, with these supported transforms:
#   ### Heading     → <h3>
#   **bold**       → <strong>
#   *italic*       → <em>
#   `code`         → <code>
#   ```python …``` → <pre><code class="python">…</code></pre>
#   | a | b |      → <table><tr><td>a</td><td>b</td></tr></table>
#
# We do NOT use st.markdown(unsafe_allow_html=True) because our own
# HTML in body would be parsed. So a tiny pass-through is safer &
# gives us total control over chip-grid styling.


def _md_inline(text: str) -> str:
    """Apply inline transforms to a single line (or paragraph)."""
    t = _html.escape(text)
    t = t.replace("**", "")  # we wrap our own <strong> below
    # We'll do a simple two-pass: even-bold and odd-italic state
    out = []
    i = 0
    bold = False
    italic = False
    code = False
    while i < len(t):
        ch = t[i]
        if ch == "*" and i + 1 < len(t) and t[i + 1] == "*":
            out.append("<strong>" if not bold else "</strong>")
            bold = not bold
            i += 2
        elif ch == "*":
            out.append("<em>" if not italic else "</em>")
            italic = not italic
            i += 1
        elif ch == "`":
            out.append("<code>" if not code else "</code>")
            code = not code
            i += 1
        else:
            out.append(ch)
            i += 1
    return "".join(out)


def _render_body_md(body_md: str) -> str:
    """Convert our markdown body to HTML with our styling hooks."""
    lines = body_md.split("\n")
    out = []
    in_list = False
    in_table = False
    in_pre = False
    pre_buf: list[str] = []
    table_buf: list[list[str]] = []

    def flush_table():
        nonlocal in_table, table_buf
        if not in_table:
            return
        if not table_buf:
            in_table = False
            return
        head = table_buf[0] if table_buf else []
        rows = table_buf[2:] if len(table_buf) >= 2 else []
        rows = [r for r in rows if any(c.strip() for c in r)]
        ths = "".join(f"<th>{_md_inline(c.strip())}</th>" for c in head)
        trs = "".join(
            "<tr>" + "".join(f"<td>{_md_inline(c.strip())}</td>" for c in r) + "</tr>"
            for r in rows
        )
        out.append(f'<table><thead><tr>{ths}</tr></thead><tbody>{trs}</tbody></table>')
        in_table = False
        table_buf = []

    for raw in lines:
        line = raw.rstrip()
        if in_pre:
            if line.startswith("```"):
                code_text = _html.escape("\n".join(pre_buf))
                out.append(f'<pre><code>{code_text}</code></pre>')
                pre_buf = []
                in_pre = False
            else:
                pre_buf.append(line)
            continue
        if line.startswith("```"):
            flush_table()
            in_pre = True
            continue
        if line.startswith("### "):
            flush_table()
            out.append(f"<h3>{_md_inline(line[4:])}</h3>")
            continue
        if line.startswith("## "):
            flush_table()
            out.append(f"<h3>{_md_inline(line[3:])}</h3>")
            continue
        if line.startswith("# "):
            flush_table()
            out.append(f"<h3>{_md_inline(line[2:])}</h3>")
            continue
        if line.startswith("- "):
            flush_table()
            if not in_list:
                out.append("<ul>")
                in_list = True
            out.append(f"<li>{_md_inline(line[2:])}</li>")
            continue
        if line.startswith("|") and "|" in line[1:]:
            cells = [c for c in line.split("|") if c != ""]
            if not in_table:
                in_table = True
                table_buf = []
            table_buf.append(cells)
            continue
        if not line.strip():
            if in_list:
                out.append("</ul>")
                in_list = False
            flush_table()
            out.append("")
            continue
        flush_table()
        if in_list:
            out.append("</ul>")
            in_list = False
        out.append(f"<p>{_md_inline(line)}</p>")
    if in_list:
        out.append("</ul>")
    flush_table()
    if in_pre:
        out.append(f'<pre><code>{_html.escape(chr(10).join(pre_buf))}</code></pre>')

    return "\n".join(out)


# ====================================================================
# Cross-refs (real links only, no AI generation)
# ====================================================================

def _load_cross_refs(chapter_id: str) -> dict:
    """Fetch news + repos + 1 prompt from the bible. Cached per chapter
    in st.session_state so we don't refetch on every Streamlit rerun."""
    cache_key = f"cr2_{chapter_id}"
    if cache_key in st.session_state:
        return st.session_state[cache_key]
    try:
        news = cr_fetch_news(chapter_id, limit=2)
    except Exception:
        news = []
    try:
        repos = cr_fetch_repos(chapter_id, limit=1)
    except Exception:
        repos = []
    prompts: list = []
    try:
        from prompts import load_prompts_index
        idx = load_prompts_index()
        prompts = cr_find_prompts(chapter_id, idx, limit=1)
    except Exception:
        pass
    cr = {
        "news": [
            {"title": x.title, "url": x.url, "src": x.source, "summary": x.summary}
            for x in news
        ],
        "repos": [
            {"title": x.title, "url": x.url, "summary": x.summary}
            for x in repos
        ],
        "prompts": [
            {"title": p.get("title", ""),
             "category": p.get("category", ""),
             "difficulty": p.get("difficulty", "")}
            for p in prompts
        ],
    }
    st.session_state[cache_key] = cr
    return cr


# ====================================================================
# Main render · the only public entry point
# ====================================================================

# ====================================================================
# Lecture-page body CSS (kept local — body typography is content-tuned
# and we don't want to spread it across multiple files).
# ====================================================================
_BODY_CSS = """
.lrn-body { font-family: Newsreader, serif; font-size: 1.08rem; line-height: 1.75; color: #f4ede0; }
.lrn-body h3 { font-family: Newsreader, serif; font-weight: 500; color: #f4ede0;
               font-size: 1.28rem; margin: 1.6rem 0 0.5rem; line-height: 1.3; }
.lrn-body p  { margin: 0 0 1rem 0; color: #d4cebf; }
.lrn-body strong { color: #f4ede0; font-weight: 600; }
.lrn-body em     { color: #d4a574; font-style: italic; }
.lrn-body code { font-family: JetBrains Mono, monospace; background: #1f1d1a;
                padding: 0.1rem 0.4rem; border-radius: 4px; font-size: 0.88em;
                color: #e8a598; }
.lrn-body pre { background: #1f1d1a; border: 1px solid #3a3530; border-radius: 8px;
                padding: 1rem; overflow-x: auto; font-family: JetBrains Mono, monospace;
                font-size: 0.82rem; line-height: 1.55; margin: 0 0 1.2rem; }
.lrn-body pre code { background: transparent; padding: 0; color: #f4ede0; }
.lrn-body ul { padding-left: 1.2rem; margin: 0 0 1rem 0; }
.lrn-body li { margin: 0.4rem 0; color: #d4cebf; }
.lrn-body table { border-collapse: collapse; margin: 1rem 0; width: 100%;
                  font-size: 0.92rem; font-family: Newsreader, serif; }
.lrn-body th { font-family: JetBrains Mono, monospace; font-size: 0.6rem;
               text-align: left; color: #8a8478; text-transform: uppercase;
               letter-spacing: 0.08em; padding: 0.6rem 0.5rem;
               border-bottom: 1px solid #3a3530; }
.lrn-body td { padding: 0.6rem 0.5rem; color: #d4cebf; border-bottom: 1px solid #2e2b27; }
.lrn-body tr:last-child td { border-bottom: none; }
"""


def render_detail_panel(
    selected_id: str,
    ch_list: list,
    completed: set,
) -> None:
    """Lecture-page renderer · PR-A layout v1.

    Single column, calm reading measure, body early. The previous
    implementation used a 3:1 two-column layout with a heavy sidebar
    counter; that chrome has been demoted into a quiet footer strip.
    The body markdown, cross-ref data fetch, verifiers, methods, and
    Ask Groq helper are kept — only their position and presentation
    have changed.
    """
    ch = get_chapter(selected_id)
    accent = domain_color(ch.domain)
    idx = next((i for i, c in enumerate(ch_list) if c.id == ch.id), 0)
    prev_ch = ch_list[idx - 1] if idx > 0 else None
    next_ch = ch_list[idx + 1] if idx < len(ch_list) - 1 else None
    total = len(ch_list)

    # ── Open the lecture column ──
    st.markdown('<div class="lrn-lecture">', unsafe_allow_html=True)

    # ── Lecture header ──
    st.markdown(
        f'<div class="lrn-breadcrumb">❡ Learning · Capitol</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="lrn-numeral" style="color:{accent};">{ch.number:02d}</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="lrn-domain-tag" style="color:{accent};">'
        f'{_html.escape(ch.domain)}'
        f'&nbsp;&nbsp;<span style="color:#6a6458;">era {_html.escape(ch.era)}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<h1 class="lrn-title">{_html.escape(ch.title)}</h1>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<p class="lrn-subtitle">{_html.escape(ch.subtitle)}</p>',
        unsafe_allow_html=True,
    )
    st.markdown('<hr class="lrn-rule" />', unsafe_allow_html=True)

    # ── Lecture body (the main experience) ──
    body_html = _render_body_md(ch.body_md)
    st.markdown(
        f'<div class="lrn-body">{body_html}</div>'
        f'<style>{_BODY_CSS}</style>',
        unsafe_allow_html=True,
    )

    # ── Build this · one calm amber callout under the body ──
    if ch.build_this:
        st.markdown('<hr class="lrn-rule" />', unsafe_allow_html=True)
        st.markdown(
            f'<div class="lrn-domain-tag" style="color:{accent};">⚡ Fă asta ACUM</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div style="font-family: Newsreader, serif; font-size: 1.1rem; '
            f'line-height: 1.65; color: #f4ede0; margin-top: 0.4rem;">'
            f'{_html.escape(ch.build_this)}</div>',
            unsafe_allow_html=True,
        )

    # ── Key takeaways · "idei de reținut" ──
    # One visible control per takeaway: a native Streamlit checkbox
    # whose label IS the takeaway text. The checkbox writes directly
    # to the same verifier_<ch.id>_<i> key that the ?p=... token
    # already round-trips, so persistence stays intact and the
    # completion auto-write below keeps working.
    if ch.verifiers:
        st.markdown('<hr class="lrn-rule" />', unsafe_allow_html=True)
        st.markdown(
            f'<div class="lrn-domain-tag" style="color:{accent};">'
            f'◌ Idei de reținut</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<p style="font-family: Newsreader, serif; font-style: italic; '
            'color: #9a8f7c; font-size: 1.02rem; line-height: 1.55; '
            'margin: 0.3rem 0 0.5rem;">'
            'Dacă pleci cu doar 3 lucruri din lecția asta, acestea sunt.'
            '</p>',
            unsafe_allow_html=True,
        )
        all_ticked = True
        for vi, v in enumerate(ch.verifiers):
            key = f"verifier_{ch.id}_{vi}"
            ticked = bool(st.session_state.get(key, False))
            if not ticked:
                all_ticked = False
            st.checkbox(v, key=key)

        if all_ticked:
            # Auto-complete (no button gate) — write directly to session_state.
            if ch.id not in completed:
                completed = set(completed) | {ch.id}
                st.session_state.completed_chapters = completed
            # Softer celebration card. No "treci la următorul" instruction —
            # the footer progress strip below already shows the next chapter.
            st.markdown(
                '<div class="lrn-completion">'
                '<div class="lrn-completion-msg">'
                'Foarte bine. Lecția asta e a ta.'
                '</div>'
                '<div class="lrn-completion-sub">'
                'idei bifate · capitol încheiat'
                '</div>'
                '</div>',
                unsafe_allow_html=True,
            )

    # ── Main method card · lifted out of the body flow ──
    if ch.methods:
        main = next((m for m in ch.methods if m.recommended), None)
        alts = [m for m in ch.methods if not m.recommended]
        if main:
            st.markdown('<hr class="lrn-rule" />', unsafe_allow_html=True)
            st.markdown(
                f'<div class="lrn-domain-tag" style="color:{accent};">'
                f'◆ Metoda recomandată</div>',
                unsafe_allow_html=True,
            )
            # Method card — single bordered surface with a left accent
            # rule. Hierarchy: tag · name · summary · "de ce funcționează".
            st.markdown(
                f'<div class="lrn-method">'
                f'<div class="lrn-method-name">{_html.escape(main.name)}</div>'
                f'<div class="lrn-method-summary">{_html.escape(main.summary)}</div>'
                + (
                    f'<div class="lrn-method-why">'
                    f'De ce funcționează: {_html.escape(main.when_to_use)}'
                    f'</div>'
                    if main.when_to_use else ''
                )
                + f'</div>',
                unsafe_allow_html=True,
            )
            st.checkbox(
                f"Am aplicat „{main.name}”",
                key=f"method_done_{ch.id}_main",
            )
        # Alts · quiet one-line disclosure instead of full expanders
        if alts:
            with st.expander(f"○ Abordări alternative ({len(alts)})", expanded=False):
                for ai, alt in enumerate(alts):
                    st.markdown(
                        f'<div style="font-family: Newsreader, serif; '
                        f'font-size: 0.98rem; color: #cdc4b1; line-height: 1.6; '
                        f'margin: 0.2rem 0 0.6rem;">'
                        f'<strong>{_html.escape(alt.name)}</strong>'
                        f'&nbsp;· {_html.escape(alt.summary)}</div>',
                        unsafe_allow_html=True,
                    )
                    st.checkbox(
                        f"Am încercat „{alt.name}”",
                        key=f"method_done_{ch.id}_alt_{ai}",
                    )

    # ── Cross-refs · moved below the body (footer area) ──
    cr = _load_cross_refs(ch.id)
    has_any = cr["news"] or cr["repos"] or cr["prompts"]
    if has_any:
        st.markdown('<hr class="lrn-rule" />', unsafe_allow_html=True)
        st.markdown(
            f'<div class="lrn-domain-tag" style="color:{accent};">'
            f'▸ De pe fluxul nostru</div>',
            unsafe_allow_html=True,
        )
        for n in cr["news"]:
            st.markdown(
                f'<div style="margin: 0.4rem 0; font-size: 0.95rem;">'
                f'<span class="lrn-footer" style="margin-right: 0.5rem;">NEWS</span>'
                f'<a href="{_html.escape(n["url"])}" target="_blank" '
                f'style="font-family: Newsreader, serif; color: #f4ede0; '
                f'text-decoration: none; border-bottom: 1px dashed #3a342c;">'
                f'{_html.escape(n["title"][:90])}</a></div>',
                unsafe_allow_html=True,
            )
        for r in cr["repos"]:
            st.markdown(
                f'<div style="margin: 0.4rem 0; font-size: 0.95rem;">'
                f'<span class="lrn-footer" style="margin-right: 0.5rem;">TOOL</span>'
                f'<a href="{_html.escape(r["url"])}" target="_blank" '
                f'style="font-family: Newsreader, serif; color: #f4ede0; '
                f'text-decoration: none; border-bottom: 1px dashed #3a342c;">'
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
                f'<span style="font-family: Newsreader, serif; color: #f4ede0;">'
                f'{_html.escape(p["title"][:90])}</span></div>',
                unsafe_allow_html=True,
            )

    # ── Ask Groq · quietly below the body (footer area) ──
    st.markdown('<hr class="lrn-rule" />', unsafe_allow_html=True)
    with st.expander(
        f"💬 Întreabă-l pe Groq · despre acest capitol",
        expanded=False,
    ):
        st.caption(
            "Asistent AI pe OpenRadar — rulează când Groq e configurat. "
            "Fără cheie, UI-ul nu se strică, dar nu primești răspuns."
        )
        ask_q = st.text_input(
            "Întrebare",
            key=f"ask_in_{ch.id}",
            placeholder="Ex: cum fac routing fără OpenRouter?",
            label_visibility="collapsed",
        )
        if ask_q and ask_q.strip():
            with st.spinner("Groq gândește..."):
                answer, ask_src = ask_groq(ask_q, ch.id)
            if answer:
                src_label = "GROQ · LIVE" if ask_src == "groq" else "DEMO"
                st.markdown(
                    f'<div style="font-family: Newsreader, serif; font-size: 1rem; '
                    f'line-height: 1.6; color: #f4ede0; margin-top: 0.6rem;">'
                    f'<span class="lrn-footer" style="margin-right: 0.5rem;">'
                    f'{src_label}</span>'
                    f'{_html.escape(answer)}</div>',
                    unsafe_allow_html=True,
                )

    # ── Next chapter · quiet one-line nudge ──
    if next_ch:
        st.markdown(
            f'<div style="margin-top: 1.6rem; padding-top: 0.8rem;">'
            f'<span class="lrn-footer">următorul ▸</span>'
            f'&nbsp;<a href="#" class="lrn-navlink" '
            f'data-next="{_html.escape(next_ch.id)}">'
            f'{next_ch.number:02d} · {_html.escape(next_ch.title)}</a></div>',
            unsafe_allow_html=True,
        )

    # ── Footer strip · one quiet progress line (was sidebar) ──
    done = len(completed)
    pct = int(done / total * 100) if total else 0
    next_label = (
        f"{next_ch.number:02d} · {next_ch.title}"
        if next_ch else "ultimul capitol"
    )
    st.markdown('<hr class="lrn-rule" />', unsafe_allow_html=True)
    st.markdown(
        f'<div class="lrn-footer">'
        f'{ch.number:02d} / {total:02d}&nbsp;&nbsp;·&nbsp;&nbsp;'
        f'{pct}% complet&nbsp;&nbsp;·&nbsp;&nbsp;'
        f'următorul: {_html.escape(next_label)}'
        f'</div>',
        unsafe_allow_html=True,
    )

    # ── Prev / Next inline nav (Streamlit buttons for state mutation) ──
    nav_cols = st.columns(2)
    with nav_cols[0]:
        if prev_ch:
            if st.button(
                f"◀ {prev_ch.title[:30]}",
                key=f"prev-{ch.id}",
                use_container_width=True,
            ):
                st.session_state.selected_chapter = prev_ch.id
                st.rerun()
    with nav_cols[1]:
        if next_ch:
            if st.button(
                f"{next_ch.title[:30]} ▶",
                key=f"next-{ch.id}",
                use_container_width=True,
            ):
                st.session_state.selected_chapter = next_ch.id
                st.rerun()

    # ── Close the lecture column ──
    st.markdown('</div>', unsafe_allow_html=True)
