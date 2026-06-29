"""Chapter tags — keywords used to match each chapter against live
feeds (News / GitHub Trending / Prompts / Jobs).

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
    "ch11": ["role", "job", "career", "engineer", "researcher", "applied"],
    "ch12": ["portfolio", "project", "build", ("github", 2.0), "demo"],
    "ch13": ["certification", "course", "learning", "credential", "exam"],
    "ch14": ["tool", "stack", "ide", "vscode", "cursor", "cli", ("agent", 2.0)],
    "ch15": ["newsletter", "podcast", "follow", "account", "stay current"],
}


def tags_for(chapter_id: str) -> list[tuple[str, float]]:
    """Return [(tag, weight), ...] for a chapter."""
    raw = CHAPTER_TAGS.get(chapter_id, [])
    out: list[tuple[str, float]] = []
    for t in raw:
        if isinstance(t, tuple):
            out.append((t[0].lower(), float(t[1])))
        else:
            out.append((t.lower(), 1.0))
    return out
