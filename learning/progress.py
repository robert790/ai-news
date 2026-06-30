"""Learning progress persistence — stdlib-only signed query-param token.

OpenRadar PR1 (`feat/persistence-progress-queryparam`).

The transport is the URL itself: every Learning action writes a compact,
optionally-signed token into ``?p=...`` via ``st.query_params``. The next
page render reads it back, validates, and restores the same set of
``session_state`` keys. No disk, no cookies, no localStorage, no new deps.

Persistence boundary (the only contract that matters):

    session_state  <--snapshot/encode-->  ?p=...  <--decode/restore-->  session_state

Why URL only:
- Survives HF Space cold starts (HF Spaces have no persistent disk).
- Survives refresh, browser-restart, and incognito paste.
- Cheap to share as a deep link.
- No new surface area (no JS-in-component, no cookie SameSite caveats).

Schema (versioned — bump SCHEMA_VERSION on incompatible changes):

    {
        "v": 1,
        "sc": "ch1",                                # selected_chapter
        "cc": ["ch1", "ch3"],                       # completed_chapters (sorted)
        "ver": {"ch1": [true, true, false], ...},   # verifier_{ch.id}_{i}
        "meth": {                                   # method_done_{ch.id}_main / _alt_{i}
            "ch1": {"main": true, "alts": [false]},
            ...
        }
    }

Deterministic ordering: all dict keys sorted; ``cc`` sorted; arrays
positional. Keeps the same logical state on two runs to produce identical
tokens.

Signing:
- ``OPENRADAR_PROGRESS_SECRET`` set → HMAC-SHA256, truncated to 16 bytes.
- Not set → unsigned dev mode. Page still loads. UI banner warns the user.

STDLIB ONLY. No ``itsdangerous``, no PyJWT, no extra deps.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import zlib
from typing import Any, Optional, Protocol


SCHEMA_VERSION = 1

# Public for tests / inspection.
KEY_SELECTED = "sc"
KEY_COMPLETED = "cc"
KEY_VERIFIERS = "ver"
KEY_METHODS = "meth"
KEY_VERSION = "v"

# Hard ceiling: anything longer is fail-safe (no progress write that
# turn, no crash). 1500 chars leaves headroom for 2k URL gates and
# Streamlit's own query-param reflection.
MAX_TOKEN_CHARS = 1500

# HMAC truncation length. 128 bits is plenty for tamper detection on
# a token that already encodes no secrets.
SIG_BYTES = 16

# Loop-guard sentinel - the encoded ?p=... token we wrote on the
# previous render. sync_query_param skips the write when the freshly
# encoded token matches this value, which prevents the update->rerun->
# update cycle that would otherwise trigger an infinite Streamlit loop
# every time we touch st.query_params to keep the URL in sync.
# Lives in session_state; pure-Python side data, never round-trips
# through the snapshot/restore surface (key is private-prefixed).
_PROGRESS_LAST_TOKEN_KEY="__last_token"

# One-shot restore marker. Once we've restored from ?p=... in a
# session, we never restore again in the same browser session -
# otherwise the post-tick rerun would overwrite the user's just-ticked
# checkbox with the snapshot baked into the URL at the previous sync.
# Cleared by browser refresh (whole session_state resets), so pasting
# the URL into a fresh tab still restores as expected.
_PROGRESS_RESTORE_DONE_KEY="__restored"


# ---------------------------------------------------------------------------
# SessionState protocol — anything that supports __getitem__/__setitem__
# works (Streamlit's SessionState, plain dicts, SimpleNamespace).
# ---------------------------------------------------------------------------


class SessionStateLike(Protocol):
    def get(self, key: str, default: Any = None) -> Any: ...
    def __setitem__(self, key: str, value: Any) -> None: ...
    def __contains__(self, key: str) -> bool: ...


# ---------------------------------------------------------------------------
# Snapshot + restore
# ---------------------------------------------------------------------------


def _truthy(value: Any) -> bool:
    """Be liberal: any truthy Streamlit value counts as ``True``."""
    return bool(value)


def snapshot(state: SessionStateLike) -> dict:
    """Read the live Learning progress out of ``state`` into a SCHEMA dict.

    Tolerant of unknown keys: we never write keys we don't recognise.
    """
    sc = state.get("selected_chapter", "ch1")
    if not isinstance(sc, str) or not sc:
        sc = "ch1"

    completed_raw = state.get("completed_chapters", set()) or set()
    if isinstance(completed_raw, (list, tuple, set, frozenset)):
        cc = sorted(c for c in completed_raw if isinstance(c, str))
    else:
        cc = []

    # We can't introspect checkbox state for unknown keys — only the keys
    # the static schema declares. So callers that want full coverage must
    # construct a snapshot from a richer state. For the live UI, we walk
    # known chapter ids (provided via Chapter list) and read the indexed
    # keys. ``snapshot_for_chapters`` is the preferred entry point.
    return {
        KEY_VERSION: SCHEMA_VERSION,
        KEY_SELECTED: sc,
        KEY_COMPLETED: cc,
        KEY_VERIFIERS: {},
        KEY_METHODS: {},
    }


def snapshot_for_chapters(state: SessionStateLike, chapters: list) -> dict:
    """Build a full snapshot using the live Chapter list as the key schema.

    Walks ``verifier_{ch.id}_{i}`` and ``method_done_{ch.id}_main`` /
    ``method_done_{ch.id}_alt_{ai}`` for every chapter so the token round-
    trips every Learning checkbox.
    """
    sc = state.get("selected_chapter", "ch1")
    if not isinstance(sc, str) or not sc:
        sc = "ch1"

    completed_raw = state.get("completed_chapters", set()) or set()
    if isinstance(completed_raw, (list, tuple, set, frozenset)):
        cc = sorted(c for c in completed_raw if isinstance(c, str))
    else:
        cc = []

    ver: dict[str, list[bool]] = {}
    meth: dict[str, dict[str, Any]] = {}

    for ch in chapters:
        ch_id = getattr(ch, "id", None) or getattr(ch, "chapter_id", None)
        if not isinstance(ch_id, str) or not ch_id:
            continue

        # Verifiers (positional array)
        verifiers = getattr(ch, "verifiers", None) or []
        if verifiers:
            ver[ch_id] = [
                _truthy(state.get(f"verifier_{ch_id}_{i}", False))
                for i in range(len(verifiers))
            ]

        # Methods: main + alts
        methods = getattr(ch, "methods", None) or []
        if methods:
            alts = [m for m in methods if not getattr(m, "recommended", False)]
            meth[ch_id] = {
                "main": _truthy(state.get(f"method_done_{ch_id}_main", False)),
                "alts": [
                    _truthy(state.get(f"method_done_{ch_id}_alt_{ai}", False))
                    for ai in range(len(alts))
                ],
            }

    return {
        KEY_VERSION: SCHEMA_VERSION,
        KEY_SELECTED: sc,
        KEY_COMPLETED: cc,
        KEY_VERIFIERS: ver,
        KEY_METHODS: meth,
    }


def restore(snap: dict, state: SessionStateLike) -> None:
    """Write a decoded snapshot back into ``state``.

    Only writes keys we recognise; never touches section / nav / facets /
    tips / cross-ref cache state.
    """
    if not isinstance(snap, dict):
        return
    if snap.get(KEY_VERSION) != SCHEMA_VERSION:
        return

    sc = snap.get(KEY_SELECTED)
    if isinstance(sc, str) and sc:
        state["selected_chapter"] = sc

    cc = snap.get(KEY_COMPLETED)
    if isinstance(cc, list):
        # Set ordering doesn't survive JSON round-trips, but Streamlit's
        # session_state accepts a list fine for the existing render code
        # (it coerces to ``| {ch.id}``).
        state["completed_chapters"] = [c for c in cc if isinstance(c, str)]

    ver = snap.get(KEY_VERIFIERS)
    if isinstance(ver, dict):
        for ch_id, arr in ver.items():
            if not isinstance(ch_id, str) or not isinstance(arr, list):
                continue
            for i, v in enumerate(arr):
                state[f"verifier_{ch_id}_{i}"] = bool(v)

    meth = snap.get(KEY_METHODS)
    if isinstance(meth, dict):
        for ch_id, payload in meth.items():
            if not isinstance(ch_id, str) or not isinstance(payload, dict):
                continue
            if "main" in payload:
                state[f"method_done_{ch_id}_main"] = bool(payload.get("main", False))
            alts = payload.get("alts")
            if isinstance(alts, list):
                for ai, v in enumerate(alts):
                    state[f"method_done_{ch_id}_alt_{ai}"] = bool(v)


# ---------------------------------------------------------------------------
# Encode + decode
# ---------------------------------------------------------------------------


def _canonical_bytes(snap: dict) -> bytes:
    """Deterministic JSON for signing. Sort keys at every level."""
    return json.dumps(
        snap,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _secret() -> bytes:
    raw = os.getenv("OPENRADAR_PROGRESS_SECRET", "")
    return raw.encode("utf-8") if raw else b""


def encode(snap: dict, *, _secret_override: Optional[bytes] = None) -> str:
    """Encode a snapshot to a URL-safe string.

    Shape (signed mode)::

        <zlib(json)>\n<sig>

    Shape (dev/unsigned mode)::

        <zlib(json)>

    Token is urlsafe-base64-encoded before either variant.

    Returns ``""`` on any error or on tokens exceeding ``MAX_TOKEN_CHARS``.
    The caller treats ``""`` as "skip this sync" — app keeps running.
    """
    try:
        if not isinstance(snap, dict):
            return ""
        # Enforce version & determinism right before serialise.
        snap = {
            KEY_VERSION: SCHEMA_VERSION,
            KEY_SELECTED: snap.get(KEY_SELECTED, "ch1"),
            KEY_COMPLETED: sorted(snap.get(KEY_COMPLETED, []) or []),
            KEY_VERIFIERS: _sort_ver(snap.get(KEY_VERIFIERS, {}) or {}),
            KEY_METHODS: _sort_meth(snap.get(KEY_METHODS, {}) or {}),
        }
        payload = _canonical_bytes(snap)
        body = zlib.compress(payload, level=9)
        encoded = base64.urlsafe_b64encode(body).rstrip(b"=").decode("ascii")
        secret = _secret_override if _secret_override is not None else _secret()
        if secret:
            sig = hmac.new(secret, body, hashlib.sha256).digest()[:SIG_BYTES]
            sig_b64 = base64.urlsafe_b64encode(sig).rstrip(b"=").decode("ascii")
            token = f"{encoded}.{sig_b64}"
        else:
            token = encoded
        if len(token) > MAX_TOKEN_CHARS:
            # Fail safe — drop the sync. App keeps running with whatever
            # state it had. Log via stderr so it's visible in CI.
            import sys
            print(
                f"[progress] token too long ({len(token)} > {MAX_TOKEN_CHARS}); skipping sync",
                file=sys.stderr,
            )
            return ""
        return token
    except Exception as exc:  # pragma: no cover - defensive
        import sys
        print(f"[progress] encode error: {exc}", file=sys.stderr)
        return ""


def decode(token: str, *, _secret_override: Optional[bytes] = None) -> Optional[dict]:
    """Decode a token. Returns the snapshot dict, or ``None`` on any error:
    empty token, bad base64, bad zlib, bad JSON, missing v, wrong v,
    tampered signature. Never raises.
    """
    if not token or not isinstance(token, str):
        return None
    try:
        secret = _secret_override if _secret_override is not None else _secret()
        encoded, sig = _split_token(token, secret)
        if encoded is None:
            return None
        try:
            body = base64.urlsafe_b64decode(encoded + "=" * (-len(encoded) % 4))
        except Exception:
            return None
        if secret:
            expected = hmac.new(secret, body, hashlib.sha256).digest()[:SIG_BYTES]
            if not hmac.compare_digest(expected, sig):
                return None
        try:
            payload = zlib.decompress(body)
        except Exception:
            return None
        try:
            snap = json.loads(payload)
        except Exception:
            return None
        if not isinstance(snap, dict):
            return None
        if snap.get(KEY_VERSION) != SCHEMA_VERSION:
            return None
        return snap
    except Exception:
        return None


def _split_token(token: str, secret: bytes) -> tuple[Optional[str], bytes]:
    """Return ``(encoded_body, sig_or_empty)``.

    For unsigned (dev-mode) tokens, ``encoded_body`` is the whole token
    and ``sig_or_empty`` is ``b""``. For invalid signed tokens
    (e.g. missing separator) returns ``(None, b"")``.
    """
    if not secret:
        return token, b""
    if "." not in token:
        return None, b""
    encoded, sig_b64 = token.rsplit(".", 1)
    try:
        sig = base64.urlsafe_b64decode(sig_b64 + "=" * (-len(sig_b64) % 4))
    except Exception:
        return None, b""
    return encoded, sig


def _sort_ver(ver: dict) -> dict:
    return {
        ch_id: list(arr) if isinstance(arr, list) else []
        for ch_id, arr in sorted(ver.items(), key=lambda kv: kv[0])
    }


def _sort_meth(meth: dict) -> dict:
    out = {}
    for ch_id, payload in sorted(meth.items(), key=lambda kv: kv[0]):
        if not isinstance(payload, dict):
            continue
        alts = payload.get("alts")
        out[ch_id] = {
            "main": bool(payload.get("main", False)),
            "alts": list(alts) if isinstance(alts, list) else [],
        }
    return out


# ---------------------------------------------------------------------------
# Streamlit integration helpers
# ---------------------------------------------------------------------------


def get_incoming_token(query_params: Any) -> Optional[str]:
    """Pull the ``p`` token out of an ``st.query_params``-like object.

    Tries attribute access first (``query_params.p`` — what real
    Streamlit prefers since 1.32), then item access (``query_params["p"]``),
    then dict ``.get()``.

    Returns the token string (first element if Streamlit returned a list)
    or ``None``. Never raises.
    """
    if query_params is None:
        return None

    token: Any = None

    # 1) Attribute access — works for ``SimpleNamespace`` and real Streamlit
    #    ``QueryParams`` proxies.
    if not token:
        try:
            token = getattr(query_params, "p", None)
        except Exception:
            token = None

    # 2) Item access — works for dict-like and some Streamlit backends.
    if not token:
        try:
            token = query_params["p"]
        except Exception:
            token = None

    # 3) Dict-style ``.get()`` for completeness.
    if not token:
        try:
            token = query_params.get("p")
        except Exception:
            token = None

    if isinstance(token, list):
        token = token[0] if token else None
    if not isinstance(token, str) or not token:
        return None
    return token


def apply_incoming_query_param(
    state: SessionStateLike,
    query_params: Any,
    *,
    warn: Optional[Any] = None,
) -> bool:
    """Restore from ``?p=...`` if a valid token is present and we
    have not already restored in this Streamlit session.

    Returns ``True`` if state was restored, ``False`` otherwise.

    Restoring is gated on a one-shot session_state marker so the
    post-tick rerun does not overwrite the user's just-ticked checkbox
    with the stale snapshot baked into the URL. The marker is cleared
    by a full browser refresh (which resets the whole session_state),
    so pasting the URL into a fresh tab still restores as expected.

    ``warn`` is optional and only used to surface a single ``st.warning``
    message when a token is present but invalid. We don't auto-strip
    ``?p=`` so the URL remains the persistence transport.
    """
    already = state.get(_PROGRESS_RESTORE_DONE_KEY, False) if hasattr(state, "get") else False
    if already:
        return False

    token = get_incoming_token(query_params)
    if token is None:
        return False
    snap = decode(token)
    if snap is None:
        if warn is not None:
            try:
                warn("Tokenul din URL nu e valid — progres existent nu s-a restaurat.")
            except Exception:
                pass
        return False
    restore(snap, state)
    try:
        state[_PROGRESS_RESTORE_DONE_KEY] = True
    except Exception:
        pass
    return True


def sync_query_param(
    state: SessionStateLike,
    query_params: Any,
    chapters: Optional[list] = None,
) -> bool:
    """Encode the current snapshot into ``?p=...``. No-op when unchanged.

    Returns ``True`` if the query param was updated, ``False`` otherwise.
    Never raises; never strips ``?p=``.

    ``chapters`` is optional. When present we walk the chapter list and
    capture all verifier/method booleans (the only way to round-trip the
    implicit checkbox keys). When absent we emit a "navigation-only"
    snapshot — still useful for the ``selected_chapter`` deep-link.
    """
    if chapters is not None:
        snap = snapshot_for_chapters(state, chapters)
    else:
        snap = snapshot(state)

    token = encode(snap)
    if not token:
        return False

    last = state.get(_PROGRESS_LAST_TOKEN_KEY) if hasattr(state, "get") else None
    if last == token:
        return False

    try:
        query_params["p"] = token
    except Exception:
        # Some Streamlit versions expose only attribute writes; try that
        # path before giving up. Failing silently is acceptable — the
        # only consequence is "this session didn't write a token", which
        # is recoverable on the next mutation.
        try:
            setattr(query_params, "p", token)  # type: ignore[attr-defined]
        except Exception:
            return False

    try:
        state[_PROGRESS_LAST_TOKEN_KEY] = token
    except Exception:
        pass
    return True
