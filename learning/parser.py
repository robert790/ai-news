"""Parse ai-beginners-guide/index.html into per-chapter HTML chunks
adapted to OpenRadar's dark theme.

We extract everything inside <section class="chapter" id="chN"> for
each of the 15 chapters (ch1..ch15) and emit a compact HTML file that
Streamlit can render with our CSS overrides (so the .callout /
.analogy / .kitchen containers match OpenRadar's palette).

Skips the glossary and resources appendix — those live in OpenRadar's
own content layer (chapters.py + tips.py).

Heavy SVGs (the chapter-1 kitchen diagram etc.) are preserved — they
help comprehension and the diagram density IS a feature.

Run from the project root:
    python -m learning.parser
"""
from __future__ import annotations

import re
from pathlib import Path

from bs4 import BeautifulSoup, NavigableString

# Path resolution: project root is parent.parent of this file.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SOURCE_HTML = Path(
    "/Users/zero/.minimax-agent/projects/ai-beginners-guide/index.html"
)
if not SOURCE_HTML.exists():
    # Fallback: same project sibling source
    alt = PROJECT_ROOT.parent / "ai-beginners-guide" / "index.html"
    if alt.exists():
        SOURCE_HTML = alt
OUTPUT_DIR = PROJECT_ROOT / "learning" / "content"

# Chapter ordering — only the 15 main chapters (skip glossary/resources).
CHAPTERS = [f"ch{i}" for i in range(1, 16)]


def _wipe_classes(tag, keep=("callout", "analogy", "kitchen")):
    """Normalize class names so we control them through OpenRadar CSS.

    Strips internal Tailwind-ish classes (e.g. `.text-grey-700`) but
    keeps the structural classes (`.callout`, `.analogy`, `.kitchen`)
    so we can style them.
    """
    if not hasattr(tag, "get"):
        return
    cls = tag.get("class") or []
    cleaned = [c for c in cls if c in keep]
    if cleaned:
        tag["class"] = cleaned
    elif "class" in tag.attrs:
        del tag["class"]


def _strip_inline_styles(soup):
    """Drop style='' attributes — we paint through CSS."""
    for tag in soup.find_all(True):
        if "style" in tag.attrs:
            # keep styles only on tags that absolutely need to (svg sizing)
            style = tag.attrs["style"]
            if "font-family" in style or "max-width" in style or "width:" in style:
                continue
            del tag.attrs["style"]


def _first_paragraph_as_lead(chapter) -> str | None:
    """Return the first big paragraph as the chapter 'lead' for our
    Reader card header (above the body)."""
    p = chapter.find("p", class_="lead")
    if p:
        return p.get_text(" ", strip=True)
    # fallback: first <p> after h2
    h2 = chapter.find("h2")
    if h2:
        sib = h2.find_next_sibling("p")
        if sib:
            return sib.get_text(" ", strip=True)
    return None


def _tagline(chapter) -> str | None:
    p = chapter.find("p", class_="tagline")
    return p.get_text(" ", strip=True) if p else None


def _chapter_num(chapter) -> str | None:
    p = chapter.find("p", class_="chapter-num")
    return p.get_text(" ", strip=True) if p else None


def _clean_for_streamlit(chapter) -> str:
    """Return an HTML string safe to render in Streamlit.

    Strips nav, footer, sticky UI. Keeps callouts, analogies,
    SVGs, paragraphs, lists, h3s.
    """
    # Clone so we don't mutate original
    cl = BeautifulSoup(str(chapter), "html.parser")

    # Remove chapter-num / h2 (those are already shown in the header)
    for sel in ["p.chapter-num", "h2", "p.tagline", "p.lead"]:
        for t in cl.select(sel):
            t.decompose()

    # Strip Tailwind-ish classes
    for tag in cl.find_all(True):
        _wipe_classes(tag)
        if tag.name == "svg":
            # Ensure svg is responsive
            tag["preserveAspectRatio"] = tag.get(
                "preserveAspectRatio", "xMidYMid meet"
            )
            if "width" not in tag.attrs and tag.get("viewBox"):
                tag["width"] = "100%"

    _strip_inline_styles(cl)
    # Tidy: collapse multiple blank lines / whitespace
    raw = str(cl)
    raw = re.sub(r"\n\s*\n+", "\n", raw)
    return raw.strip()


def parse_one(chapter_soup) -> dict:
    """Return a dict describing one chapter, ready for Streamlit."""
    return {
        "id": chapter_soup.get("id", ""),
        "num": _chapter_num(chapter_soup),
        "title": chapter_soup.find("h2").get_text(strip=True).rstrip(".") if chapter_soup.find("h2") else "",
        "tagline": _tagline(chapter_soup),
        "lead": _first_paragraph_as_lead(chapter_soup),
        "body_html": _clean_for_streamlit(chapter_soup),
    }


def parse_all(source: Path = SOURCE_HTML) -> dict[str, dict]:
    html = source.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")
    out = {}
    for cid in CHAPTERS:
        section = soup.find("section", id=cid)
        if not section:
            continue
        out[cid] = parse_one(section)
    return out


# --------------------------------------------------------------
# CSS injected alongside each chapter's HTML — adapts the source
# course's beige-paper aesthetic to OpenRadar's dark theme.
# --------------------------------------------------------------
READER_CSS = """
<style>
  .lrn-reader {
    font-family: 'Newsreader', Georgia, serif;
    color: #f4ede0;
    line-height: 1.7;
    font-size: 1.02rem;
  }
  .lrn-reader p {
    margin: 0 0 1rem 0;
    color: #d4cebf;
  }
  .lrn-reader p strong {
    color: #f4ede0;
    font-weight: 600;
  }
  .lrn-reader p em { color: #d4a574; font-style: italic; }

  .lrn-reader h3 {
    font-family: 'Newsreader', Georgia, serif;
    font-weight: 500;
    color: #f4ede0;
    font-size: 1.25rem;
    margin: 1.5rem 0 0.6rem;
    line-height: 1.3;
  }
  .lrn-reader ul, .lrn-reader ol {
    color: #d4cebf;
    margin: 0 0 1.1rem 1.4rem;
    padding-left: 0.4rem;
  }
  .lrn-reader li {
    margin-bottom: 0.45rem;
    line-height: 1.6;
  }
  .lrn-reader li::marker { color: #6a6458; }
  .lrn-reader a {
    color: #d4a574;
    text-decoration: none;
    border-bottom: 1px dashed rgba(212, 165, 116, 0.35);
  }
  .lrn-reader a:hover {
    border-bottom-style: solid;
  }
  .lrn-reader code {
    font-family: 'JetBrains Mono', monospace;
    background: #1f1d1a;
    padding: 0.1rem 0.4rem;
    border-radius: 4px;
    font-size: 0.9em;
    color: #e8a598;
  }
  .lrn-reader pre {
    background: #1f1d1a;
    border: 1px solid #3a3530;
    border-radius: 8px;
    padding: 1rem;
    overflow-x: auto;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.85rem;
    line-height: 1.55;
    margin: 0 0 1.2rem;
  }
  .lrn-reader pre code {
    background: transparent;
    padding: 0;
    color: #f4ede0;
  }

  /* The source course's .callout (gold accent) */
  .lrn-reader .callout {
    background: rgba(212, 165, 116, 0.07);
    border-left: 2px solid #d4a574;
    border-radius: 0 8px 8px 0;
    padding: 0.9rem 1.1rem;
    margin: 1.1rem 0;
    font-size: 1rem;
    line-height: 1.6;
    color: #f4ede0;
  }
  .lrn-reader .callout strong {
    color: #d4a574;
    font-weight: 600;
  }

  /* The source course's .analogy (teal accent + mono header) */
  .lrn-reader .analogy {
    background: rgba(168, 192, 174, 0.04);
    border: 1px solid rgba(168, 192, 174, 0.18);
    border-radius: 10px;
    padding: 0.5rem 1.1rem 1rem;
    margin: 1.1rem 0;
  }
  .lrn-reader .analogy-head {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.62rem;
    color: #a8c0ae;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin: 0.7rem 0 0.4rem;
    padding: 0;
    background: transparent;
    border: none;
  }
  .lrn-reader .analogy-head svg { color: #a8c0ae; }
  .lrn-reader .analogy h3 {
    font-family: 'Newsreader', Georgia, serif;
    color: #f4ede0;
    margin: 0.4rem 0 0.4rem;
    font-size: 1.1rem;
  }
  .lrn-reader .analogy p {
    color: #d4cebf;
    font-size: 0.98rem;
    margin-bottom: 0.7rem;
  }
  .lrn-reader .analogy .real {
    background: rgba(168, 192, 174, 0.06);
    border-left: 2px solid #a8c0ae;
    padding: 0.55rem 0.8rem;
    border-radius: 0 6px 6px 0;
    color: #c4d6c8;
    margin-top: 0.7rem;
  }
  .lrn-reader .analogy .real strong { color: #a8c0ae; }

  /* The kitchen SVG wrapper — keep proportionally sized */
  .lrn-reader .kitchen {
    background: #1f1d1a;
    border: 1px solid #3a3530;
    border-radius: 12px;
    padding: 1rem;
    margin: 1.2rem 0;
    text-align: center;
  }
  .lrn-reader .kitchen svg {
    width: 100%;
    height: auto;
    max-width: 800px;
    display: block;
    margin: 0 auto;
  }
  .lrn-reader .kitchen-caption {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    color: #8a8478;
    margin-top: 0.6rem;
    text-align: center;
    letter-spacing: 0.04em;
  }

  /* Standalone SVGs (not inside .kitchen) */
  .lrn-reader > svg {
    width: 100%;
    max-width: 640px;
    height: auto;
    display: block;
    margin: 1rem auto;
  }

  /* Mobile parity */
  @media (max-width: 640px) {
    .lrn-reader { font-size: 0.98rem; }
    .lrn-reader pre { font-size: 0.78rem; padding: 0.8rem; }
  }
</style>
"""


def write_chunks(chunks: dict[str, dict], dest: Path = OUTPUT_DIR) -> list[Path]:
    dest.mkdir(parents=True, exist_ok=True)
    written = []
    for cid, data in chunks.items():
        # Save as plain HTML for inspection, plus a "render-ready" variant
        # that embeds the reader CSS so Streamlit can render directly.
        if data is None:
            continue
        rendered = (
            READER_CSS
            + f'<div class="lrn-reader" id="{cid}-reader">{data["body_html"]}</div>'
        )
        out_html = dest / f"{cid}.html"
        out_meta = dest / f"{cid}.json"
        out_html.write_text(rendered, encoding="utf-8")
        out_meta.write_text(
            __import__("json").dumps(
                {
                    "id": data["id"],
                    "num": data["num"],
                    "title": data["title"],
                    "tagline": data["tagline"],
                    "lead": data["lead"],
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        written.append(out_html)
        written.append(out_meta)
    return written


def main():
    chunks = parse_all()
    written = write_chunks(chunks)
    print(f"Parsed {len(chunks)} chapters, wrote {len(written)} files to {OUTPUT_DIR}")
    # Print summary
    for cid, data in chunks.items():
        words = len(re.findall(r"\b\w+\b", data["body_html"]))
        print(
            f"  {cid:>4} | {data['num'] or '?':>10} | {data['title'][:40]:<40} | "
            f"tagline={'Y' if data['tagline'] else 'N'} "
            f"lead={'Y' if data['lead'] else 'N'} "
            f"words={words}"
        )


if __name__ == "__main__":
    main()
