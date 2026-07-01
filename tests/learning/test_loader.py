"""Tests for ``learning.loader`` - JSONL primary, Python module fallback.

All tests are pure-stdlib + pytest; no Streamlit server required.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest


# ---------------------------------------------------------------------------
# Imports under test
# ---------------------------------------------------------------------------


def test_loader_imports_match_spec():
    """The loader exposes exactly the public API the rest of the project
    imports from ``learning.chapters``."""
    from learning.loader import (
        load_chapters,
        get_all_chapters,
        get_chapter,
        get_root_id,
        reload_chapters,
        ChapterSourceError,
        JSONL_PATH,
    )

    # module-level constant exists and points at content/chapters.jsonl
    assert JSONL_PATH.name == "chapters.jsonl"
    assert JSONL_PATH.parent.name == "content"


# ---------------------------------------------------------------------------
# Happy path: JSONL present, chapters 1..10
# ---------------------------------------------------------------------------


def test_load_chapters_returns_exactly_ten():
    from learning.loader import load_chapters
    chapters = load_chapters()
    assert len(chapters) == 10
    ids = [c.id for c in chapters]
    assert ids == [f"ch{i}" for i in range(1, 11)]


def test_load_chapters_ids_are_in_declaration_order():
    from learning.loader import load_chapters
    chapters = load_chapters()
    for idx, ch in enumerate(chapters, start=1):
        assert ch.id == f"ch{idx}", f"row {idx} has id {ch.id!r}"
        assert ch.number == idx
        assert ch.title  # non-empty


def test_get_chapter_known_id_returns_dataclass():
    from learning.loader import get_chapter, load_chapters
    ch5 = get_chapter("ch5")
    assert ch5.id == "ch5"
    assert ch5.title == "Diffusion & Generative Media"
    assert len(ch5.verifiers) >= 1
    assert any(m.recommended for m in ch5.methods)


def test_get_chapter_missing_raises_keyerror():
    from learning.loader import get_chapter
    with pytest.raises(KeyError) as excinfo:
        get_chapter("ch42")
    assert "ch42" in str(excinfo.value)


def test_get_root_id_returns_first_chapter():
    from learning.loader import get_root_id, load_chapters
    assert get_root_id() == load_chapters()[0].id == "ch1"


def test_get_all_chapters_returns_a_new_list_each_call():
    """A defensive copy - callers should not mutate the loader cache."""
    from learning.loader import get_all_chapters
    a = get_all_chapters()
    b = get_all_chapters()
    assert a == b
    assert a is not b


# ---------------------------------------------------------------------------
# Field-level equivalence with the legacy Python module
# ---------------------------------------------------------------------------


def test_loader_output_field_equal_to_legacy_module():
    """Each field of each Chapter loaded from the JSONL must equal the
    corresponding field of the legacy ``learning.chapters.CHAPTERS``
    entry. Methods are compared as ordered lists because their order
    encodes the recommended-first convention used by the renderer.
    """
    from learning.chapters import CHAPTERS as LEGACY
    from learning.loader import load_chapters

    legacy_by_id = {ch.id: ch for ch in LEGACY}
    chapters = load_chapters()

    for ch in chapters:
        ref = legacy_by_id[ch.id]
        # Scalar / list fields
        assert ch.id == ref.id
        assert ch.number == ref.number
        assert ch.title == ref.title
        assert ch.subtitle == ref.subtitle
        assert ch.domain == ref.domain
        assert ch.era == ref.era
        assert ch.body_md == ref.body_md
        assert ch.build_this == ref.build_this
        assert list(ch.prereqs) == list(ref.prereqs)
        assert list(ch.verifiers) == list(ref.verifiers)

        # Methods: same length, same names in order, same flags and strings
        assert len(ch.methods) == len(ref.methods), (
            f"methods count mismatch for {ch.id}"
        )
        for m_loaded, m_ref in zip(ch.methods, ref.methods):
            assert m_loaded.name == m_ref.name
            assert m_loaded.summary == m_ref.summary
            assert m_loaded.when_to_use == m_ref.when_to_use
            assert bool(m_loaded.recommended) == bool(m_ref.recommended)


# ---------------------------------------------------------------------------
# Tags boundary: ch1..ch10 active, ch11..ch15 retired
# ---------------------------------------------------------------------------


def test_chapter_tags_active_keys_are_exactly_ch1_to_ch10():
    from learning.chapter_tags import CHAPTER_TAGS
    keys = set(CHAPTER_TAGS.keys())
    assert keys == {f"ch{i}" for i in range(1, 11)}, keys


def test_chapter_tags_retired_chapter_ids_constant_exists_and_complete():
    from learning.chapter_tags import RETIRED_CHAPTER_IDS
    assert isinstance(RETIRED_CHAPTER_IDS, frozenset)
    assert RETIRED_CHAPTER_IDS == frozenset({f"ch{i}" for i in range(11, 16)})


@pytest.mark.parametrize("retired_id", [f"ch{i}" for i in range(11, 16)])
def test_tags_for_retired_returns_empty(retired_id):
    from learning.chapter_tags import tags_for
    assert tags_for(retired_id) == []


@pytest.mark.parametrize("active_id", [f"ch{i}" for i in range(1, 11)])
def test_tags_for_active_returns_non_empty(active_id):
    from learning.chapter_tags import tags_for
    assert tags_for(active_id) != [], active_id


# ---------------------------------------------------------------------------
# JSONL fallback: missing file -> legacy CHAPTERS
# ---------------------------------------------------------------------------


def test_missing_jsonl_falls_back_to_legacy_module(tmp_path, monkeypatch):
    """If ``content/chapters.jsonl`` is missing, the loader imports
    ``learning.chapters.CHAPTERS`` instead of raising.
    """
    # Re-import the loader pointing at a non-existent file. The cleanest
    # way to test the fallback is to relocate the JSONL_PATH via
    # monkeypatch and reload the module.
    from learning import loader

    fake_root = tmp_path / "proj"
    fake_root.mkdir()
    fake_content = fake_root / "content"
    fake_content.mkdir()  # empty - no chapters.jsonl

    monkeypatch.setattr(loader, "JSONL_PATH", fake_content / "chapters.jsonl")
    loader.load_chapters.cache_clear()

    chapters = loader.load_chapters()
    assert len(chapters) == 10
    assert chapters[0].id == "ch1"
    assert chapters[-1].id == "ch10"


def test_existing_jsonl_takes_precedence_over_legacy(tmp_path, monkeypatch):
    """Even if the legacy CHAPTERS existed, an on-disk JSONL with
    different content wins (the loader is JSONL-primary)."""
    from learning import loader

    fake_root = tmp_path / "proj2"
    fake_root.mkdir()
    fake_content = fake_root / "content"
    fake_content.mkdir()
    jsonl = fake_content / "chapters.jsonl"
    jsonl.write_text(
        '{"id":"ch1","number":1,"title":"Override","subtitle":"sub","'
        'domain":"history","era":"x","prereqs":[],"body_md":"hi","'
        'build_this":"do it","verifiers":[],"methods":[]}\n',
        encoding="utf-8",
    )

    monkeypatch.setattr(loader, "JSONL_PATH", jsonl)
    loader.load_chapters.cache_clear()

    chapters = loader.load_chapters()
    assert len(chapters) == 1
    assert chapters[0].title == "Override"


# ---------------------------------------------------------------------------
# Malformed JSONL -> clear error with line number
# ---------------------------------------------------------------------------


def test_malformed_jsonl_raises_chapter_source_error_with_line_number(tmp_path, monkeypatch):
    from learning import loader
    from learning.loader import ChapterSourceError

    fake_content = tmp_path / "content"
    fake_content.mkdir()
    jsonl = fake_content / "chapters.jsonl"
    # Line 1: valid. Line 2: invalid JSON.
    jsonl.write_text(
        '{"id":"ch1","number":1,"title":"OK","subtitle":"","'
        'domain":"history","era":"","prereqs":[],"body_md":"",'
        '"build_this":"","verifiers":[],"methods":[]}\n'
        "this line is not JSON\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(loader, "JSONL_PATH", jsonl)
    loader.load_chapters.cache_clear()

    with pytest.raises(ChapterSourceError) as excinfo:
        loader.load_chapters()
    msg = str(excinfo.value)
    assert "line 2" in msg, msg


def test_non_object_jsonl_line_raises_clear_error(tmp_path, monkeypatch):
    from learning import loader
    from learning.loader import ChapterSourceError

    fake_content = tmp_path / "content"
    fake_content.mkdir()
    jsonl = fake_content / "chapters.jsonl"
    jsonl.write_text('"just a string, not an object"\n', encoding="utf-8")

    monkeypatch.setattr(loader, "JSONL_PATH", jsonl)
    loader.load_chapters.cache_clear()

    with pytest.raises(ChapterSourceError) as excinfo:
        loader.load_chapters()
    assert "str" in str(excinfo.value).lower()


def test_empty_jsonl_raises(tmp_path, monkeypatch):
    from learning import loader
    from learning.loader import ChapterSourceError

    fake_content = tmp_path / "content"
    fake_content.mkdir()
    jsonl = fake_content / "chapters.jsonl"
    jsonl.write_text("", encoding="utf-8")

    monkeypatch.setattr(loader, "JSONL_PATH", jsonl)
    loader.load_chapters.cache_clear()

    with pytest.raises(ChapterSourceError):
        loader.load_chapters()


# ---------------------------------------------------------------------------
# Public API compat through ``learning.__init__``
# ---------------------------------------------------------------------------


def test_learning_package_reexports_match_legacy_names():
    """All names ``learning/__init__.py`` previously exposed for the
    chapter API must remain importable with the same semantics.
    """
    from learning import (
        get_all_chapters,
        get_chapter,
        get_root_id,
        CHAPTERS,
        DOMAIN_META,
        COMPLEXITY_META,
        Chapter,
        domain_color,
    )

    chapters = get_all_chapters()
    assert len(chapters) == 10
    assert get_chapter("ch1").id == "ch1"
    assert get_root_id() == "ch1"
    # The legacy constant still works (deprecated but present).
    assert len(CHAPTERS) == 10
    assert DOMAIN_META["history"]["label"] == "Istoric"
    # Cross-module imports still resolve.
    assert hasattr(Chapter, "__dataclass_fields__")


# ---------------------------------------------------------------------------
# Export-script smoke
# ---------------------------------------------------------------------------


def test_export_chapters_is_deterministic(tmp_path):
    """Two consecutive runs of ``export_chapters`` produce byte-identical
    output. We don't write into the real content/ directory during
    the test - we point the script at a temp path."""
    out = tmp_path / "chapters.jsonl"

    # Run the export script twice into the same target.
    sys.path.insert(0, str(Path.cwd()))
    import importlib

    exp_a = importlib.import_module("learning.export_chapters")
    n_a = exp_a.export_chapters(out)
    first = out.read_bytes()

    # Reload to ensure any module-level caches reset; the dataclasses
    # don't have caches, but the path module-state may in other scripts.
    importlib.reload(exp_a)
    exp_b = importlib.import_module("learning.export_chapters")
    n_b = exp_b.export_chapters(out)
    second = out.read_bytes()

    assert n_a == n_b == 10
    assert first == second


def test_export_chapters_id_order_matches_declaration_order(tmp_path):
    """The export refuses to write a row whose position does not match
    its declared id (chapter index convention is 'row i -> ch{i}').
    """
    out = tmp_path / "chapters.jsonl"
    from learning import export_chapters

    n = export_chapters.export_chapters(out)
    assert n == 10
    lines = out.read_text(encoding="utf-8").splitlines()
    ids = [json.loads(line)["id"] for line in lines if line.strip()]
    assert ids == [f"ch{i}" for i in range(1, 11)]


def test_export_chapters_field_order_is_stable(tmp_path):
    """JSON object keys are written in a fixed canonical order so
    git diffs stay focused on the actual content changes."""
    out = tmp_path / "chapters.jsonl"
    from learning import export_chapters

    export_chapters.export_chapters(out)
    rows = [
        json.loads(line) for line in out.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    expected_keys = (
        "id", "number", "title", "subtitle", "domain", "era",
        "prereqs", "body_md", "build_this", "verifiers", "methods",
    )
    for row in rows:
        keys = list(row.keys())
        assert keys[: len(expected_keys)] == list(expected_keys), (
            f"first fields should be canonical; got {keys[:5]}"
        )
