"""PR10 import + dispatch smoke test.

The OpenRadar `app.py` is the Streamlit entrypoint and is the file that
takes the most repo-wide refactors. This test pins the *contract* — not
the data — so we know the UI shell still wires after any rename/restyle:

  • `app.py` imports cleanly (no top-level crash).
  • DISPATCH still routes every internal section id (groq, news,
    learning, jobs, prompts) — preserving `?section=` deep-links.
  • The five `render_*` functions are all present.
  • The new prompt-kit additions (PR10) are exposed at module scope.

This is intentionally NOT a UI snapshot test. It is an invariant test on
the routing surface. If this fails, the WebUI is broken before you even
opened it.
"""
from __future__ import annotations

import importlib
import sys
from pathlib import Path


REQUIRED_DISPATCH_KEYS = {"groq", "news", "learning", "jobs", "prompts"}
REQUIRED_RENDER_FUNCS = {
    "render_groq",
    "render_news",
    "render_learning",
    "render_jobs",
    "render_prompts",
}
PR10_PUBLIC_API = {"KITS", "kits_for"}


def _ensure_app_on_path():
    """Add repo root to sys.path so `import app` resolves from any cwd."""
    repo_root = Path(__file__).resolve().parent.parent
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))


def test_app_imports_cleanly():
    _ensure_app_on_path()
    m = importlib.import_module("app")
    # Module surface — must exist.
    assert m is not None


def test_dispatch_shape_invariant():
    _ensure_app_on_path()
    m = importlib.import_module("app")
    assert hasattr(m, "DISPATCH"), "DISPATCH dict is gone — UI routing is broken"
    assert set(m.DISPATCH) == REQUIRED_DISPATCH_KEYS, (
        f"DISPATCH keys drifted: got {sorted(m.DISPATCH)}, "
        f"expected {sorted(REQUIRED_DISPATCH_KEYS)}"
    )
    for key, fn in m.DISPATCH.items():
        assert callable(fn), f"DISPATCH[{key!r}] is not callable"


def test_render_functions_present():
    _ensure_app_on_path()
    m = importlib.import_module("app")
    missing = REQUIRED_RENDER_FUNCS - set(dir(m))
    assert not missing, f"Missing renderers: {missing}"


def test_pr10_kits_api_exposed():
    """PR10 added Prompt Kits (KITS constant + kits_for helper).

    Confirms the new product surface is reachable from app's module
    namespace, so the kits row in `render_prompts` always resolves.
    """
    _ensure_app_on_path()
    m = importlib.import_module("app")
    for name in PR10_PUBLIC_API:
        assert hasattr(m, name), (
            f"PR10 surface lost: app.{name} missing. "
            f"Kits row will break at runtime."
        )


def test_kits_helper_returns_bundles():
    """Kits helper must return a list of dicts with `id` and `prompts`."""
    from prompts import KITS, kits_for, load_prompt_bible

    bible = load_prompt_bible()
    bundles = kits_for(bible)

    assert isinstance(bundles, list)
    assert len(bundles) == len(KITS)
    for b in bundles:
        assert "id" in b and isinstance(b["id"], str)
        assert "prompts" in b and isinstance(b["prompts"], list)
        # Each kit should have at least one prompt (fallback covers empty cats).
        assert len(b["prompts"]) >= 1, (
            f"Kit {b.get('id', '?')} rendered no prompts — bible lookup broken."
        )
