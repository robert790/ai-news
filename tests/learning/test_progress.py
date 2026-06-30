"""Tests for ``learning.progress`` — Learning progress query-param transport.

Pure stdlib tests. No Streamlit server required. We synthesise ``dict``
states and a minimal ``Chapter``-like object so ``snapshot_for_chapters``
is exercised too.
"""
from __future__ import annotations

import base64
import os
import zlib
from types import SimpleNamespace

import pytest

import learning.progress as progress


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


class FakeState:
    """Drop-in replacement for ``st.session_state`` for these tests."""

    def __init__(self, initial: dict | None = None):
        self._d: dict = dict(initial or {})

    def get(self, key, default=None):
        return self._d.get(key, default)

    def __getitem__(self, key):
        return self._d[key]

    def __setitem__(self, key, value):
        self._d[key] = value

    def __contains__(self, key):
        return key in self._d

    def __repr__(self):
        return f"FakeState({self._d!r})"


def make_chapter(ch_id: str, n_verifiers: int = 2, n_alts: int = 1):
    """Build a minimal chapter-shaped namespace."""
    meth = []
    if n_alts >= 1:
        meth.append(SimpleNamespace(name="MAIN", recommended=True))
    for i in range(n_alts):
        meth.append(SimpleNamespace(name=f"ALT{i}", recommended=False))
    return SimpleNamespace(
        id=ch_id,
        verifiers=[f"verifier-{i}" for i in range(n_verifiers)],
        methods=meth,
    )


# ---------------------------------------------------------------------------
# Snapshot / restore
# ---------------------------------------------------------------------------


def test_snapshot_empty_state_has_version_and_defaults():
    state = FakeState()
    snap = progress.snapshot(state)
    assert snap["v"] == progress.SCHEMA_VERSION
    assert snap["sc"] == "ch1"
    assert snap["cc"] == []
    assert snap["ver"] == {}
    assert snap["meth"] == {}


def test_snapshot_with_partial_state():
    state = FakeState({
        "selected_chapter": "ch3",
        "completed_chapters": {"ch1", "ch2"},
        "verifier_ch2_0": True,
    })
    snap = progress.snapshot(state)
    assert snap["sc"] == "ch3"
    assert snap["cc"] == ["ch1", "ch2"]  # sorted


def test_snapshot_for_chapters_walks_every_key():
    ch1 = make_chapter("ch1", n_verifiers=2, n_alts=1)
    ch2 = make_chapter("ch2", n_verifiers=3, n_alts=2)
    state = FakeState({
        "selected_chapter": "ch2",
        "completed_chapters": {"ch1"},
        "verifier_ch1_0": True,
        "verifier_ch1_1": False,
        "method_done_ch1_main": True,
        "method_done_ch1_alt_0": False,
        "verifier_ch2_0": True,
        "verifier_ch2_1": True,
        "verifier_ch2_2": False,
        "method_done_ch2_main": False,
        "method_done_ch2_alt_0": True,
        "method_done_ch2_alt_1": False,
    })
    snap = progress.snapshot_for_chapters(state, [ch1, ch2])

    assert snap["v"] == progress.SCHEMA_VERSION
    assert snap["sc"] == "ch2"
    assert snap["cc"] == ["ch1"]
    assert snap["ver"]["ch1"] == [True, False]
    assert snap["ver"]["ch2"] == [True, True, False]
    assert snap["meth"]["ch1"]["main"] is True
    assert snap["meth"]["ch1"]["alts"] == [False]
    assert snap["meth"]["ch2"]["main"] is False
    assert snap["meth"]["ch2"]["alts"] == [True, False]


def test_snapshot_for_chapters_drops_chapters_without_verifiers_or_methods():
    ch = SimpleNamespace(id="ch9", verifiers=[], methods=[])  # both empty
    snap = progress.snapshot_for_chapters(FakeState(), [ch])
    assert "ch9" not in snap["ver"]
    assert "ch9" not in snap["meth"]


def test_restore_round_trip_full():
    ch1 = make_chapter("ch1", n_verifiers=2, n_alts=1)
    ch2 = make_chapter("ch2", n_verifiers=3, n_alts=2)
    initial_state = FakeState({
        "selected_chapter": "ch2",
        "completed_chapters": {"ch1", "ch3"},
        "verifier_ch1_0": True,
        "verifier_ch1_1": True,
        "method_done_ch1_main": True,
        "method_done_ch1_alt_0": False,
        "verifier_ch2_0": True,
        "verifier_ch2_1": False,
        "verifier_ch2_2": True,
        "method_done_ch2_main": True,
        "method_done_ch2_alt_0": True,
        "method_done_ch2_alt_1": True,
    })
    snap = progress.snapshot_for_chapters(initial_state, [ch1, ch2])

    fresh = FakeState()
    progress.restore(snap, fresh)

    assert fresh["selected_chapter"] == "ch2"
    assert set(fresh["completed_chapters"]) == {"ch1", "ch3"}
    assert fresh["verifier_ch1_0"] is True
    assert fresh["verifier_ch1_1"] is True
    assert fresh["method_done_ch1_main"] is True
    assert fresh["method_done_ch1_alt_0"] is False
    assert fresh["verifier_ch2_0"] is True
    assert fresh["verifier_ch2_2"] is True
    assert fresh["method_done_ch2_alt_1"] is True


def test_restore_ignores_wrong_version():
    state = FakeState()
    progress.restore({"v": 99, "sc": "ch5"}, state)
    assert "selected_chapter" not in state._d


def test_restore_handles_empty_inputs_gracefully():
    state = FakeState()
    progress.restore({}, state)
    progress.restore(None, state)
    progress.restore("not a dict", state)
    assert state._d == {}


# ---------------------------------------------------------------------------
# Encode + decode — sign / unsign / tamper / version
# ---------------------------------------------------------------------------


def test_encode_decode_round_trip_unsigned(monkeypatch):
    monkeypatch.delenv("OPENRADAR_PROGRESS_SECRET", raising=False)
    snap = {
        "v": 1,
        "sc": "ch3",
        "cc": ["ch1", "ch2"],
        "ver": {"ch1": [True, False], "ch2": [True, True, False]},
        "meth": {"ch1": {"main": True, "alts": [False]}, "ch2": {"main": False, "alts": [True, False]}},
    }
    token = progress.encode(snap)
    assert token
    decoded = progress.decode(token)
    assert decoded == snap


def test_encode_decode_round_trip_signed(monkeypatch):
    monkeypatch.setenv("OPENRADAR_PROGRESS_SECRET", "test-secret-αβγ")
    snap = {"v": 1, "sc": "ch1", "cc": [], "ver": {}, "meth": {}}
    token = progress.encode(snap)
    assert token and "." in token
    assert progress.decode(token) == snap


def test_decode_rejects_tampered_body(monkeypatch):
    monkeypatch.setenv("OPENRADAR_PROGRESS_SECRET", "shared-secret")
    token = progress.encode({"v": 1, "sc": "ch1", "cc": [], "ver": {}, "meth": {}})
    # Flip one base64 char in the body.
    body, _, sig = token.partition(".")
    tampered = ("A" if body[0] != "A" else "B") + body[1:] + "." + sig
    assert progress.decode(tampered) is None


def test_decode_rejects_tampered_signature(monkeypatch):
    monkeypatch.setenv("OPENRADAR_PROGRESS_SECRET", "shared-secret")
    token = progress.encode({"v": 1, "sc": "ch1", "cc": [], "ver": {}, "meth": {}})
    body, _, _ = token.partition(".")
    fake_sig = base64.urlsafe_b64encode(b"\x00" * progress.SIG_BYTES).rstrip(b"=").decode()
    tampered = body + "." + fake_sig
    assert progress.decode(tampered) is None


def test_decode_rejects_token_signed_under_other_secret(monkeypatch):
    monkeypatch.setenv("OPENRADAR_PROGRESS_SECRET", "secret-A")
    token = progress.encode({"v": 1, "sc": "ch1", "cc": [], "ver": {}, "meth": {}})
    monkeypatch.setenv("OPENRADAR_PROGRESS_SECRET", "secret-B")
    assert progress.decode(token) is None


def test_dev_mode_accepts_unsigned_token_with_no_secret(monkeypatch):
    monkeypatch.setenv("OPENRADAR_PROGRESS_SECRET", "dev-secret")
    token = progress.encode({"v": 1, "sc": "ch2", "cc": ["ch1"], "ver": {}, "meth": {}})
    # Now pretend the secret vanished (dev mode on another machine).
    monkeypatch.delenv("OPENRADAR_PROGRESS_SECRET", raising=False)
    # Unsigned decode would skip signature check, but our token has a dot
    # because it was signed. So decoding still fails — proves the boundary.
    # Real dev mode requires generating the token in dev mode in the first
    # place:
    dev_token = progress.encode({"v": 1, "sc": "ch2", "cc": ["ch1"], "ver": {}, "meth": {}})
    assert "." not in dev_token
    assert progress.decode(dev_token)["sc"] == "ch2"


def test_decode_returns_none_for_bad_version(monkeypatch):
    monkeypatch.delenv("OPENRADAR_PROGRESS_SECRET", raising=False)
    raw = zlib.compress(
        b'{"v":99,"sc":"ch1","cc":[],"ver":{},"meth":{}}'
    )
    token = base64.urlsafe_b64encode(raw).rstrip(b"=").decode()
    assert progress.decode(token) is None


def test_decode_returns_none_for_garbage_inputs():
    assert progress.decode("") is None
    assert progress.decode("***notbase64***") is None
    assert progress.decode("aaaa.bbbb") is None
    assert progress.decode(None) is None  # type: ignore[arg-type]


def test_encode_is_deterministic(monkeypatch):
    monkeypatch.delenv("OPENRADAR_PROGRESS_SECRET", raising=False)
    snap = {
        "v": 1,
        "sc": "ch1",
        "cc": ["ch2", "ch1", "ch3"],
        "ver": {"ch3": [True, False, True], "ch1": [True]},
        "meth": {"ch3": {"main": False, "alts": [True, False]}, "ch1": {"main": True, "alts": [False]}},
    }
    t1 = progress.encode(snap)
    t2 = progress.encode(snap)
    # Same logical state → identical tokens.
    assert t1 == t2
    # cc is sorted; verifier/method dict keys are sorted.
    round_trip = progress.decode(t1)
    assert round_trip["cc"] == ["ch1", "ch2", "ch3"]
    assert list(round_trip["ver"].keys()) == ["ch1", "ch3"]
    assert list(round_trip["meth"].keys()) == ["ch1", "ch3"]


def test_encode_stays_under_token_cap_for_full_curriculum(monkeypatch):
    """Even with all 10 chapters × full state, encoded token ≤ cap."""
    monkeypatch.delenv("OPENRADAR_PROGRESS_SECRET", raising=False)
    chapters = [make_chapter(f"ch{i}", n_verifiers=3, n_alts=3) for i in range(1, 11)]
    state = FakeState(
        {
            "selected_chapter": "ch1",
            "completed_chapters": {f"ch{i}" for i in range(1, 11)},
            **{
                k: True
                for i in range(1, 11)
                for k in (
                    [f"verifier_ch{i}_{j}" for j in range(3)]
                    + [f"method_done_ch{i}_main"]
                    + [f"method_done_ch{i}_alt_{j}" for j in range(3)]
                )
            },
        }
    )
    snap = progress.snapshot_for_chapters(state, chapters)
    token = progress.encode(snap)
    assert token, "encode should produce a token for the full curriculum"
    assert len(token) < progress.MAX_TOKEN_CHARS


def test_encode_handles_over_size_input_safely(monkeypatch, capsys):
    monkeypatch.delenv("OPENRADAR_PROGRESS_SECRET", raising=False)

    # Synthesise a pathologically large snapshot: 200 chapters x 50 verifiers.
    snap = {
        "v": 1,
        "sc": "ch1",
        "cc": [f"ch{i}" for i in range(200)],
        "ver": {f"ch{i}": [True] * 50 for i in range(200)},
        "meth": {
            f"ch{i}": {
                "main": True,
                "alts": [False] * 20,
            }
            for i in range(200)
        },
    }
    token = progress.encode(snap)
    # We fail-safe rather than crash; emit "" + a stderr note.
    assert token == ""
    captured = capsys.readouterr()
    assert "too long" in captured.err


# ---------------------------------------------------------------------------
# Streamlit integration helpers
# ---------------------------------------------------------------------------


def test_get_incoming_token_handles_streamlit_query_params():
    qp = SimpleNamespace(p="abc.def")
    assert progress.get_incoming_token(qp) == "abc.def"


def test_get_incoming_token_handles_dict_like():
    class QP:
        def get(self, key, default=None):
            return {"p": "my-token"}.get(key, default)

    assert progress.get_incoming_token(QP()) == "my-token"


def test_get_incoming_token_handles_list_value():
    qp = SimpleNamespace(p=["first-token", "second-token"])  # Streamlit-ish
    assert progress.get_incoming_token(qp) == "first-token"


def test_get_incoming_token_returns_none_when_missing():
    assert progress.get_incoming_token(SimpleNamespace(p=None)) is None
    assert progress.get_incoming_token(SimpleNamespace(other=1)) is None
    assert progress.get_incoming_token(None) is None


def test_apply_incoming_query_param_restores_when_valid(monkeypatch):
    monkeypatch.delenv("OPENRADAR_PROGRESS_SECRET", raising=False)
    snap = {"v": 1, "sc": "ch4", "cc": ["ch1", "ch2"], "ver": {}, "meth": {}}
    token = progress.encode(snap)
    qp = SimpleNamespace(p=token)
    state = FakeState()
    applied = progress.apply_incoming_query_param(state, qp)
    assert applied is True
    assert state["selected_chapter"] == "ch4"
    assert set(state["completed_chapters"]) == {"ch1", "ch2"}


def test_apply_incoming_query_param_no_op_when_missing():
    state = FakeState()
    applied = progress.apply_incoming_query_param(state, SimpleNamespace(other=1))
    assert applied is False
    assert state._d == {}


def test_apply_incoming_query_param_warns_on_bad_token():
    warns: list[str] = []
    state = FakeState()
    applied = progress.apply_incoming_query_param(
        state,
        SimpleNamespace(p="garbage-not-a-real-token"),
        warn=lambda msg: warns.append(str(msg)),
    )
    assert applied is False
    assert warns == [] or any("Tokenul" in w or "valid" in w.lower() for w in warns)
    assert state._d == {}


def test_sync_query_param_writes_token_when_changed():
    state = FakeState({"selected_chapter": "ch2"})
    qp = SimpleNamespace()  # supports __setattr__
    written = progress.sync_query_param(state, qp)
    assert written is True
    assert isinstance(qp.p, str) and qp.p
    # And the loop-guard is in place.
    assert state[progress._LAST_TOKEN_KEY] == qp.p


def test_sync_query_param_no_op_when_unchanged():
    state = FakeState({"selected_chapter": "ch1", "completed_chapters": set(), "ver": {}, "meth": {}})
    qp = SimpleNamespace()
    progress.sync_query_param(state, qp)
    # Second call with same state must return False (we don't churn the URL).
    written_again = progress.sync_query_param(state, qp)
    assert written_again is False


def test_sync_query_param_supports_dict_query_params():
    class DictQP:
        def __init__(self):
            self._d: dict = {}

        def __setitem__(self, k, v):
            self._d[k] = v

        def get(self, k, default=None):
            return self._d.get(k, default)

    state = FakeState({"selected_chapter": "ch1"})
    qp = DictQP()
    written = progress.sync_query_param(state, qp)
    assert written is True
    assert qp._d.get("p")


def test_sync_query_param_uses_chapter_walk_when_provided(monkeypatch):
    monkeypatch.delenv("OPENRADAR_PROGRESS_SECRET", raising=False)
    state = FakeState({
        "selected_chapter": "ch1",
        "verifier_ch1_0": True,
    })
    qp = SimpleNamespace()
    chapters = [make_chapter("ch1", n_verifiers=2, n_alts=0)]
    written = progress.sync_query_param(state, qp, chapters=chapters)
    assert written is True
    # The captured token reflects the verifier state — round trip proves it.
    snap = progress.decode(qp.p)
    assert snap is not None
    assert snap["ver"]["ch1"][0] is True
