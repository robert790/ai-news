"""Learning · detail-panel renderer · OpenRadar v1.0 redesign.

This module owns the entire "what you see when a chapter is open"
experience: header, body markdown render, cross-refs (real links,
no AI generation), Ask Azi Q&A (the ONLY place Groq is used for
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
from learning.insight import ask_azi


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

def render_detail_panel(
    selected_id: str,
    ch_list: list,
    completed: set,
) -> None:
    ch = get_chapter(selected_id)
    accent = domain_color(ch.domain)

    # =====================
    # Header strip
    # =====================
    st.markdown(
        f'<a id="chapter-detail"></a>',
        unsafe_allow_html=True,
    )
    st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)

    st.markdown(
        f'<div style="display: flex; align-items: center; gap: 0.85rem; '
        f'flex-wrap: wrap; margin-bottom: 0.5rem;">'
        f'<span style="font-family: Newsreader, serif; font-size: 3rem; '
        f'color: {accent}; line-height: 1; font-weight: 300;">'
        f'{ch.number:02d}</span>'
        f'<div>'
        f'<div style="font-family: JetBrains Mono, monospace; font-size: 0.65rem; '
        f'color: {accent}; letter-spacing: 0.1em; text-transform: uppercase;">'
        f'{_html.escape(ch.domain)}</div>'
        f'<div style="font-family: JetBrains Mono, monospace; font-size: 0.55rem; '
        f'color: #6a6458; letter-spacing: 0.08em; margin-top: 0.15rem;">'
        f'ERA {_html.escape(ch.era)}</div>'
        f'</div>'
        f'</div>'
        f'<h2 style="margin: 0; font-family: Newsreader, serif; '
        f'font-weight: 500; line-height: 1.15;">'
        f'{_html.escape(ch.title)}</h2>'
        f'<p style="font-family: Newsreader, serif; font-style: italic; '
        f'color: #c4b9a7; font-size: 1.05rem; margin: 0.4rem 0 0 0; '
        f'line-height: 1.5;">'
        f'{_html.escape(ch.subtitle)}</p>',
        unsafe_allow_html=True,
    )

    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

    cols = st.columns([3, 1])

    # =====================
    # LEFT · body + cross-refs + Ask Azi + verifiers + build this
    # =====================
    with cols[0]:
        with st.container(border=True):
            # --- Body markdown (rendered via our own parser, NOT
            #     st.markdown, so our h3/code/table styling wins) ---
            body_html = _render_body_md(ch.body_md)
            st.markdown(
                f'<div class="lrn-body">'
                f'{body_html}'
                f'</div>'
                f'<style>'
                f'.lrn-body {{ font-family: Newsreader, serif; '
                f'font-size: 1.05rem; line-height: 1.7; color: #f4ede0; }}'
                f'.lrn-body h3 {{ font-family: Newsreader, serif; '
                f'font-weight: 500; color: #f4ede0; font-size: 1.22rem; '
                f'margin: 1.5rem 0 0.5rem; line-height: 1.3; }}'
                f'.lrn-body p {{ margin: 0 0 1rem 0; color: #d4cebf; }}'
                f'.lrn-body strong {{ color: #f4ede0; font-weight: 600; }}'
                f'.lrn-body em {{ color: #d4a574; font-style: italic; }}'
                f'.lrn-body code {{ font-family: JetBrains Mono, monospace; '
                f'background: #1f1d1a; padding: 0.1rem 0.4rem; '
                f'border-radius: 4px; font-size: 0.88em; color: #e8a598; }}'
                f'.lrn-body pre {{ background: #1f1d1a; '
                f'border: 1px solid #3a3530; border-radius: 8px; '
                f'padding: 1rem; overflow-x: auto; '
                f'font-family: JetBrains Mono, monospace; font-size: 0.82rem; '
                f'line-height: 1.55; margin: 0 0 1.2rem; }}'
                f'.lrn-body pre code {{ background: transparent; '
                f'padding: 0; color: #f4ede0; }}'
                f'.lrn-body ul {{ padding-left: 1.2rem; margin: 0 0 1rem 0; }}'
                f'.lrn-body li {{ margin: 0.4rem 0; color: #d4cebf; }}'
                f'.lrn-body table {{ border-collapse: collapse; margin: 1rem 0; '
                f'width: 100%; font-size: 0.92rem; font-family: Newsreader, serif; }}'
                f'.lrn-body th {{ font-family: JetBrains Mono, monospace; '
                f'font-size: 0.6rem; text-align: left; color: #8a8478; '
                f'text-transform: uppercase; letter-spacing: 0.08em; '
                f'padding: 0.6rem 0.5rem; border-bottom: 1px solid #3a3530; }}'
                f'.lrn-body td {{ padding: 0.6rem 0.5rem; color: #d4cebf; '
                f'border-bottom: 1px solid #2e2b27; }}'
                f'.lrn-body tr:last-child td {{ border-bottom: none; }}'
                f'</style>',
                unsafe_allow_html=True,
            )

            # --- Cross-refs (real, no AI gen) ---
            cr = _load_cross_refs(ch.id)
            has_any = cr["news"] or cr["repos"] or cr["prompts"]
            if has_any:
                st.markdown(
                    f'<div style="margin-top: 1.5rem; padding-top: 1.2rem; '
                    f'border-top: 1px solid #2e2b27;">'
                    f'<div style="font-family: JetBrains Mono, monospace; '
                    f'font-size: 0.65rem; color: {accent}; '
                    f'letter-spacing: 0.1em; text-transform: uppercase; '
                    f'margin-bottom: 0.7rem;">'
                    f'▸ Din fluxul nostru · legat de acest capitol</div>',
                    unsafe_allow_html=True,
                )
                for n in cr["news"]:
                    st.markdown(
                        f'<div style="padding: 0.5rem 0.7rem; '
                        f'background: rgba(168, 192, 174, 0.04); '
                        f'border-radius: 5px; margin-bottom: 0.4rem; '
                        f'border-left: 2px solid #a8c0ae38;">'
                        f'<span style="font-family: JetBrains Mono, monospace; '
                        f'font-size: 0.55rem; color: #a8c0ae; '
                        f'margin-right: 0.5rem;">'
                        f'NEWS · {_html.escape(n["src"].upper().replace("_", " "))}</span>'
                        f'<a href="{_html.escape(n["url"])}" target="_blank" '
                        f'style="font-family: Newsreader, serif; color: #f4ede0; '
                        f'font-size: 0.92rem; text-decoration: none; '
                        f'border-bottom: 1px dashed rgba(168,192,174,0.4);">'
                        f'{_html.escape(n["title"][:90])}</a>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
                for r in cr["repos"]:
                    st.markdown(
                        f'<div style="padding: 0.5rem 0.7rem; '
                        f'background: rgba(232, 165, 152, 0.04); '
                        f'border-radius: 5px; margin-bottom: 0.4rem; '
                        f'border-left: 2px solid #e8a59838;">'
                        f'<span style="font-family: JetBrains Mono, monospace; '
                        f'font-size: 0.55rem; color: #e8a598; '
                        f'margin-right: 0.5rem;">'
                        f'TOOL</span>'
                        f'<a href="{_html.escape(r["url"])}" target="_blank" '
                        f'style="font-family: Newsreader, serif; color: #f4ede0; '
                        f'font-size: 0.92rem; text-decoration: none; '
                        f'border-bottom: 1px dashed rgba(232,165,152,0.4);">'
                        f'{_html.escape(r["title"])}</a>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
                for p in cr["prompts"]:
                    st.markdown(
                        f'<div style="padding: 0.5rem 0.7rem; '
                        f'background: rgba(212, 165, 116, 0.04); '
                        f'border-radius: 5px; margin-bottom: 0.4rem; '
                        f'border-left: 2px solid #d4a57438;">'
                        f'<span style="font-family: JetBrains Mono, monospace; '
                        f'font-size: 0.55rem; color: #d4a574; '
                        f'margin-right: 0.5rem;">'
                        f'PROMPT BIBLE · {_html.escape((p["category"] or "?").upper())} · '
                        f'{_html.escape((p["difficulty"] or "?").upper())}</span>'
                        f'<span style="font-family: Newsreader, serif; '
                        f'color: #f4ede0; font-size: 0.92rem;">'
                        f'{_html.escape(p["title"][:90])}</span>'
                        f'<div style="font-family: JetBrains Mono, monospace; '
                        f'font-size: 0.55rem; color: #6a6458; margin-top: 0.25rem;">'
                        f'→ deschide tab-ul Prompts</div>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
                st.markdown("</div>", unsafe_allow_html=True)

            # --- Ask Azi · the ONLY place Groq is used in Learning ---
            with st.expander("💬 Întreabă-l pe Azi · despre acest capitol", expanded=False):
                st.caption(
                    "Azi e asistentul tău AI pe OpenRadar. Groq (Llama 3.1 8B) "
                    "răspunde live la întrebări despre AI în general și "
                    "despre capitolul ăsta."
                )
                ask_key = f"ask_in_{ch.id}"
                ask_q = st.text_input(
                    "Întrebare",
                    key=ask_key,
                    placeholder="Ex: cum fac routing fără OpenRouter?",
                    label_visibility="collapsed",
                )
                if ask_q and ask_q.strip():
                    with st.spinner("Azi gândește..."):
                        answer, ask_src = ask_azi(ask_q, ch.id)
                    if answer:
                        src_label = "GROQ · LIVE" if ask_src == "groq" else "DEMO"
                        st.markdown(
                            f'<div style="font-family: Newsreader, serif; '
                            f'font-size: 1rem; line-height: 1.6; color: #f4ede0; '
                            f'margin-top: 0.6rem; padding: 0.8rem 1rem; '
                            f'background: rgba(244, 237, 224, 0.03); '
                            f'border-radius: 6px; border-left: 2px solid {accent};">'
                            f'<span style="color: {accent}; margin-right: 0.5rem; '
                            f'font-family: JetBrains Mono, monospace; font-size: 0.7rem;">'
                            f'AZI · {src_label}</span>'
                            f'{_html.escape(answer)}'
                            f'</div>',
                            unsafe_allow_html=True,
                        )

            # --- Verifiers ---
            if ch.verifiers:
                st.markdown(
                    f'<div style="margin-top: 1.5rem; padding-top: 1.2rem; '
                    f'border-top: 1px solid #2e2b27;">'
                    f'<div style="font-family: JetBrains Mono, monospace; '
                    f'font-size: 0.65rem; color: #a8c0ae; '
                    f'letter-spacing: 0.1em; text-transform: uppercase; '
                    f'margin-bottom: 0.6rem;">'
                    f'▸ Ai înțeles? bifează tot</div>',
                    unsafe_allow_html=True,
                )
                for vi, v in enumerate(ch.verifiers):
                    k = f"verifier_{ch.id}_{vi}"
                    st.checkbox(v, key=k)
                all_ticked = all(
                    st.session_state.get(f"verifier_{ch.id}_{vi}", False)
                    for vi in range(len(ch.verifiers))
                )
                if all_ticked:
                    already = ch.id in completed
                    if not already:
                        if st.button(
                            "✓ Marchează capitolul complet",
                            key=f"complete_{ch.id}",
                            type="primary",
                            use_container_width=True,
                        ):
                            st.session_state.completed_chapters = completed | {ch.id}
                            st.rerun()
                    else:
                        st.markdown(
                            '<span style="font-family: JetBrains Mono, monospace; '
                            'font-size: 0.65rem; color: #a8c0ae;">'
                            '✓ Capitol complet · treci la următorul</span>',
                            unsafe_allow_html=True,
                        )
                st.markdown("</div>", unsafe_allow_html=True)

            # --- Build this ---
            if ch.build_this:
                st.markdown(
                    f'<div style="margin-top: 1.5rem; padding: 1rem 1.2rem; '
                    f'background: rgba(212, 165, 116, 0.06); '
                    f'border-left: 2px solid #d4a574; '
                    f'border-radius: 0 8px 8px 0;">'
                    f'<div style="font-family: JetBrains Mono, monospace; '
                    f'font-size: 0.62rem; color: #d4a574; '
                    f'letter-spacing: 0.1em; text-transform: uppercase; '
                    f'margin-bottom: 0.5rem;">⚡ Fă asta ACUM</div>'
                    f'<div style="font-family: Newsreader, serif; '
                    f'font-size: 1.02rem; line-height: 1.6; color: #f4ede0;">'
                    f'{_html.escape(ch.build_this)}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

        # --- Prev / Next ---
        idx = next((i for i, c in enumerate(ch_list) if c.id == ch.id), 0)
        prev_ch = ch_list[idx - 1] if idx > 0 else None
        next_ch = ch_list[idx + 1] if idx < len(ch_list) - 1 else None

        nav_cols = st.columns(2)
        with nav_cols[0]:
            if prev_ch:
                if st.button(
                    f"← {prev_ch.title[:22]}",
                    key=f"prev-{ch.id}",
                    use_container_width=True,
                ):
                    st.session_state.selected_chapter = prev_ch.id
                    st.rerun()
        with nav_cols[1]:
            if next_ch:
                if st.button(
                    f"{next_ch.title[:22]} →",
                    key=f"next-{ch.id}",
                    use_container_width=True,
                ):
                    st.session_state.selected_chapter = next_ch.id
                    st.rerun()

    # =====================
    # RIGHT · sidebar meta
    # =====================
    with cols[1]:
        with st.container(border=True):
            done = len(completed)
            total = len(ch_list)
            pct = int(done / total * 100) if total else 0
            st.markdown(
                f'<div style="font-family: JetBrains Mono, monospace; '
                f'font-size: 0.6rem; color: {accent}; '
                f'letter-spacing: 0.1em; text-transform: uppercase; '
                f'margin-bottom: 0.5rem;">'
                f'▸ Capitolul {ch.number:02d} din {total}</div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<div style="font-family: Newsreader, serif; '
                f'font-size: 0.95rem; color: #c4b9a7; line-height: 1.55;">'
                f'Ești în drumul spre Project Erica. {total - ch.number} '
                f'capitole rămase până la final.</div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<div style="margin-top: 1rem; padding-top: 0.8rem; '
                f'border-top: 1px solid #2e2b27;">'
                f'<div style="font-family: JetBrains Mono, monospace; '
                f'font-size: 0.6rem; color: {accent}; '
                f'letter-spacing: 0.1em; text-transform: uppercase;">'
                f'PROGRES · {done}/{total} ({pct}%)</div>'
                f'<div style="margin-top: 0.4rem; height: 4px; '
                f'background: #2e2b27; border-radius: 2px; overflow: hidden;">'
                f'<div style="width: {pct}%; height: 100%; '
                f'background: {accent}; transition: width 350ms ease;"></div>'
                f'</div></div>',
                unsafe_allow_html=True,
            )

            # Cozy closed-state message
            if ch.id == ch_list[0].id:
                st.markdown(
                    '<p style="font-family: Newsreader, serif; font-style: italic; '
                    'color: #8a8478; font-size: 0.85rem; margin-top: 1rem; '
                    'line-height: 1.5;">'
                    'Începe cu Project Erica. Nu citi totul — fă primul '
                    '"Build this" și treci la 02.</p>',
                    unsafe_allow_html=True,
                )
