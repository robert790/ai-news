"""Regenerate ``content/chapters.jsonl`` from ``learning/chapters.py``.

The authoritative chapter list lives in :mod:`learning.chapters` for this
release. The JSONL file in ``content/chapters.jsonl`` is the preferred
editor-facing source for future content work; this script rebuilds the
JSONL file from the Python source so the two stay byte-identical.

Run from the project root::

    python -m learning.export_chapters

Determinism contract:

- Output is one JSON object per line, in ``CHAPTERS`` declaration order.
- Object keys are emitted in a fixed order (``id, number, title, subtitle,
  domain, era, prereqs, body_md, build_this, verifiers, methods``) so
  git diffs are stable.
- Method order on each chapter is preserved (NAME then RECOMMENDED
  inside the same array slot).
- Field values are JSON-canonical: ``ensure_ascii=False`` so the
  Romanian diacritics stay human-readable; ``indent=None`` and a single
  space after ``:`` to keep each line compact but parseable.

Hard invariants enforced:

- Exactly ``len(CHAPTERS)`` rows are written; if this number changes
  the script raises ``RuntimeError`` (the editorial caller is
  expected to bump the schema in ``loader.py`` alongside).
- Each row's ``id`` matches the chapter's ``.id``; the export refuses to
  produce a JSONL where row index != chapter position.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from learning.chapters import CHAPTERS, Chapter, Method


# Field order chosen for stable diffs; do NOT reorder without bumping
# schema in loader.py and announcing the migration.
_FIELD_ORDER = (
    "id",
    "number",
    "title",
    "subtitle",
    "domain",
    "era",
    "prereqs",
    "body_md",
    "build_this",
    "verifiers",
    "methods",
)

# Path is resolved relative to the project root, not the cwd, so the
# script works from any invocation context.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DEST = PROJECT_ROOT / "content" / "chapters.jsonl"


def _chapter_to_dict(ch: Chapter) -> dict:
    return {
        "id": ch.id,
        "number": ch.number,
        "title": ch.title,
        "subtitle": ch.subtitle,
        "domain": ch.domain,
        "era": ch.era,
        "prereqs": list(ch.prereqs),
        "body_md": ch.body_md,
        "build_this": ch.build_this,
        "verifiers": list(ch.verifiers),
        "methods": [
            {
                "name": m.name,
                "summary": m.summary,
                "when_to_use": m.when_to_use,
                "recommended": bool(m.recommended),
            }
            for m in ch.methods
        ],
    }


def _ordered_dict(d: dict) -> dict:
    """Return a dict with keys in the canonical order; unknown keys
    fall to the end (alphabetised) so they never silently disappear.
    """
    known = {k: d[k] for k in _FIELD_ORDER if k in d}
    extras = {k: d[k] for k in d if k not in _FIELD_ORDER}
    extras = {k: extras[k] for k in sorted(extras)}
    known.update(extras)
    return known


def export_chapters(dest: Path = DEFAULT_DEST) -> int:
    """Write the current ``CHAPTERS`` list as JSONL to ``dest``.

    Returns the number of rows written.
    """
    rows = []
    for idx, ch in enumerate(CHAPTERS):
        if ch.id != f"ch{idx + 1}":
            raise RuntimeError(
                f"CHAPTERS[{idx}].id is {ch.id!r}; expected ch{idx + 1}. "
                "JSONL order is enforced to match declaration order."
            )
        rows.append(_ordered_dict(_chapter_to_dict(ch)))

    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open("w", encoding="utf-8", newline="\n") as f:
        for row in rows:
            f.write(
                json.dumps(row, ensure_ascii=False, separators=(",", ": "))
            )
            f.write("\n")
    return len(rows)


def main() -> int:
    n = export_chapters()
    print(f"Wrote {n} chapters to {DEFAULT_DEST}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
