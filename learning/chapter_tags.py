"""Chapter tags — keywords used to match each chapter against live
feeds (News / GitHub Trending / Prompts / Jobs).

Active chapter ids: ``ch1..ch10``. The legacy entries ``ch11..ch15``
were retired in PR2 (June 2026) when the chapter surface was moved
to ``content/chapters.jsonl``. Their static content still lives in
``learning/content/chN.{html,json}`` for archive purposes; see
``content/retired_chapters.json`` for the full retirement note.

``tags_for(retired_id)`` returns ``[]`` so cross-ref scoring treats
retired ids as silent no-ops. A future PR may revive some of these
chapters; the JSONL id convention is ``chN`` so a revived chapter
can be added by appending a JSONL row and re-introducing the tag
entry here.

Hand-curated, NOT generated. Quality > automation here: if the tags
don't feel like the chapter, cross-refs feel random and the moat
breaks.

Add 3-6 keywords per chapter — mix of domain nouns (e.g. "neural
network", "llm", "romania", "rag") and the kind of words real
people use in posts (e.g. "prompt", "cuda", "agent").

Match-mode: case-insensitive substring across the item title +
summary + tags. Score is sum of tag hits (more hits = stronger match).
"""
from __future__ import annotations

# Format: chapter_id -> list[str | tuple[str, weight]]
# Optional weight (default 1.0) for tags that should rank higher.
CHAPTER_TAGS: dict[str, list[str | tuple[str, float]]] = {
    "ch1": ["neural network", "machine learning", "ml", "kitchen", "deep learning"],
    "ch2": ["openai", "sam altman", "chatgpt", "gpt", "startup"],
    "ch3": ["deepseek", "china", "ai race", "model", "training"],
    "ch4": ["business", "adopt", "strategy", "industry", "enterprise"],
    "ch5": ["prompt", "prompting", "chain of thought", "few-shot",
            "rag", "system prompt", "instruction"],
    "ch6": ["paper", "research", "arxiv", "transformer", "benchmark"],
    "ch7": ["action", "week 1", "first steps", "begin", "starter"],
    "ch8": ["gpu", "cluster", "romania", "infrastructure", "nvidia",
            "hpc", "compute"],
    "ch9": ["romania", "startup", "company", "ecosystem", "team"],
    "ch10": ["opportunity", "gap", "niche", "market", ("positioning", 2.0)],
}

# Retired chapter ids — present in the chapter_tags surface for
# backward-compat only. Live UI uses ch1..ch10; legacy ch11..ch15
# prose exists only as static HTML/JSON in learning/content/ and is
# not reachable from the active UI.
RETIRED_CHAPTER_IDS: frozenset[str] = frozenset({
    "ch11",  # role/job/career (legacy)
    "ch12",  # portfolio/project/build (legacy)
    "ch13",  # certification/course (legacy)
    "ch14",  # tool/stack/IDE (legacy)
    "ch15",  # newsletter/podcast/follow (legacy)
})


def tags_for(chapter_id: str) -> list[tuple[str, float]]:
    """Return ``[(tag, weight), ...]`` for a chapter.

    Retired chapter ids (see ``RETIRED_CHAPTER_IDS``) return an empty
    list — the cross-ref scorer treats them as silent no-ops so a
    stale ``chapter_id`` does not pollute the live news cross-refs.
    """
    if chapter_id in RETIRED_CHAPTER_IDS:
        return []
    raw = CHAPTER_TAGS.get(chapter_id, [])
    out: list[tuple[str, float]] = []
    for t in raw:
        if isinstance(t, tuple):
            out.append((t[0].lower(), float(t[1])))
        else:
            out.append((t.lower(), 1.0))
    return out
