"""Chapter content loader — JSONL primary source, Python module fallback.

The preferred editable source for chapter content is
``content/chapters.jsonl``. This module:

1. Reads ``content/chapters.jsonl`` once per process and instantiates
   :class:`~learning.chapters.Chapter` dataclasses.
2. Falls back to :data:`~learning.chapters.CHAPTERS` when the JSONL
   file is missing so dev environments without the file still work.
3. Raises a clear, line-numbered error when the JSONL exists but is
   malformed.
4. Avoids Streamlit imports so it stays unit-testable.

Public API mirrors what the rest of the project already imports from
``learning.chapters``:

- ``load_chapters()`` -> list[Chapter]
- ``get_all_chapters()`` -> list[Chapter]
- ``get_chapter(id: str)`` -> Chapter
- ``get_root_id()`` -> str

The loader caches its result with ``functools.lru_cache(maxsize=1)``
so repeated calls in the same process are free. If the JSONL file
changes mid-process, callers can call :func:`reload_chapters` to bust
the cache (one-shot escape hatch; not used by the app code today).
"""
from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path
from typing import List

from learning.chapters import Chapter, Method

# Path is resolved relative to the project root, not the cwd, so the
# loader works from any invocation context.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
JSONL_PATH = PROJECT_ROOT / "content" / "chapters.jsonl"


class ChapterSourceError(RuntimeError):
    """Raised when the JSONL exists but is malformed.

    The error includes the offending line number for editor-side
    diagnosis. The :class:`loader` never raises bare ``ValueError`` or
    ``json.JSONDecodeError`` so callers can catch one specific error
    type.
    """


def _build_chapter(row: dict) -> Chapter:
    methods = [
        Method(
            name=str(m.get("name", "")),
            summary=str(m.get("summary", "")),
            when_to_use=str(m.get("when_to_use", "")),
            recommended=bool(m.get("recommended", False)),
        )
        for m in (row.get("methods") or [])
    ]
    return Chapter(
        id=str(row["id"]),
        number=int(row["number"]),
        title=str(row.get("title", "")),
        subtitle=str(row.get("subtitle", "")),
        body_md=str(row.get("body_md", "")),
        verifiers=list(row.get("verifiers") or []),
        build_this=str(row.get("build_this", "")),
        prereqs=list(row.get("prereqs") or []),
        domain=str(row.get("domain", "concepts")),
        era=str(row.get("era", "")),
        methods=methods,
    )


def _read_jsonl(path: Path) -> List[Chapter]:
    chapters: List[Chapter] = []
    text = path.read_text(encoding="utf-8")
    for line_no, raw in enumerate(text.splitlines(), start=1):
        if not raw.strip():
            continue
        try:
            row = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ChapterSourceError(
                f"Failed to parse {path} line {line_no}: {exc.msg} "
                f"(line preview: {raw[:80]!r})"
            ) from exc
        if not isinstance(row, dict):
            raise ChapterSourceError(
                f"Line {line_no} of {path} is {type(row).__name__}, "
                "expected a JSON object"
            )
        try:
            chapters.append(_build_chapter(row))
        except (KeyError, TypeError, ValueError) as exc:
            raise ChapterSourceError(
                f"Failed to build Chapter from {path} line {line_no}: "
                f"{exc} (line preview: {raw[:80]!r})"
            ) from exc
    if not chapters:
        raise ChapterSourceError(
            f"{path} is empty; expected at least one Chapter row"
        )
    return chapters


def _chapter_id_already_exists(exc: KeyError) -> str | None:
    """Best-effort extraction of the colliding id from a KeyError raised
    inside ``_build_chapter``. Returns ``None`` when the cause is
    something else (e.g. a missing ``id`` field).
    """
    if exc.args and isinstance(exc.args[0], str):
        return exc.args[0]
    return None


def _from_fallback() -> List[Chapter]:
    """Lazy import the legacy module so the loader has no circular-import
    hazard at module-import time."""
    from learning.chapters import CHAPTERS  # late import; testable

    return list(CHAPTERS)


def _load() -> List[Chapter]:
    if JSONL_PATH.exists():
        try:
            chapters = _read_jsonl(JSONL_PATH)
        except ChapterSourceError:
            # Let the explicit schema-error bubble up; never silently
            # fall back when the file exists but is broken - that
            # would hide editor mistakes.
            raise
        # Belt-and-braces: enforce declaration-order id convention.
        for idx, ch in enumerate(chapters):
            expected = f"ch{idx + 1}"
            if ch.id != expected:
                raise ChapterSourceError(
                    f"Row {idx + 1} of {JSONL_PATH} has id {ch.id!r}; "
                    f"expected {expected!r}. Chapter order must match "
                    "the JSONL declaration order."
                )
        return chapters
    return _from_fallback()


@lru_cache(maxsize=1)
def load_chapters() -> List[Chapter]:
    """Return the canonical chapter list. Cached for the lifetime of
    the process."""
    return _load()


def get_all_chapters() -> List[Chapter]:
    return list(load_chapters())


def get_chapter(chapter_id: str) -> Chapter:
    for ch in load_chapters():
        if ch.id == chapter_id:
            return ch
    raise KeyError(f"Unknown chapter: {chapter_id}")


def get_root_id() -> str:
    return load_chapters()[0].id


def reload_chapters() -> List[Chapter]:
    """Bust the cache and re-read from disk. Use after editing the
    JSONL during a long-running process; not invoked by the app.
    """
    load_chapters.cache_clear()
    return load_chapters()


__all__ = [
    "JSONL_PATH",
    "ChapterSourceError",
    "load_chapters",
    "get_all_chapters",
    "get_chapter",
    "get_root_id",
    "reload_chapters",
]
