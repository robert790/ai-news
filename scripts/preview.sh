#!/usr/bin/env bash
# OpenRadar PR preview server.
#
# One standard command, one standard port (8780) for VPS-hosted PR
# visual QA. Mac tunnels to it; HF live is separate and unaffected.
#
# See docs/WORKFLOW.md for the full convention.

set -euo pipefail

PORT="${PORT:-8780}"
HOST="${HOST:-127.0.0.1}"
APP_FILE="app.py"

# ── 1. Repo + branch sanity ────────────────────────────────────────────
if [[ ! -d .git ]]; then
  echo "✗ not a git repo (cwd: $(pwd))" >&2
  exit 1
fi

BRANCH="$(git rev-parse --abbrev-ref HEAD)"
COMMIT_SHORT="$(git rev-parse --short HEAD)"
COMMIT_LONG="$(git rev-parse HEAD)"
echo "✓ repo OK · branch=$BRANCH · commit=$COMMIT_SHORT"

# ── 2. Refuse if 8780 is held by a non-OpenRadar process ────────────────
# Only act on listeners whose python cmdline literally contains
# 'streamlit run app.py' bound to this port. Hermes (9119) and any
# unrelated service on 8780 are left alone.
if ss -ltnp 2>/dev/null | grep -E ":${PORT}\b" >/dev/null; then
  HOLDER_PID="$(ss -ltnp 2>/dev/null | grep -E ":${PORT}\b" | grep -oE 'pid=[0-9]+' | head -1 | cut -d= -f2 || true)"
  if [[ -n "${HOLDER_PID:-}" ]] && ps -p "$HOLDER_PID" -o args= 2>/dev/null | grep -q "streamlit run ${APP_FILE}"; then
    echo "✓ $PORT already running OpenRadar Streamlit (pid $HOLDER_PID) — re-using" >&2
    ALREADY_UP=1
  else
    echo "✗ port $PORT is held by a non-OpenRadar process (pid ${HOLDER_PID:-?})" >&2
    echo "  stop it first, or set PORT=<other>" >&2
    exit 1
  fi
else
  ALREADY_UP=0
fi

# ── 3. Start (or skip start if already up) ─────────────────────────────
if [[ "${ALREADY_UP}" -eq 0 ]]; then
  : > preview.log
  nohup ./.venv/bin/python -m streamlit run "${APP_FILE}" \
      --server.address "${HOST}" \
      --server.port "${PORT}" \
      --server.headless true \
      --browser.gatherUsageStats false \
      >> preview.log 2>&1 &
  SPAWN_PID=$!
  echo "✓ spawned (parent pid $SPAWN_PID) — waiting for streamlit to bind"

  # Wait up to 15s for the port to come up.
  UP=0
  for _ in $(seq 1 30); do
    sleep 0.5
    if curl -fsS "http://${HOST}:${PORT}/_stcore/health" >/dev/null 2>&1; then
      UP=1
      break
    fi
  done

  if [[ "${UP}" -ne 1 ]]; then
    echo "✗ streamlit did not become healthy on ${HOST}:${PORT} within 15s" >&2
    echo "  last 20 lines of preview.log:" >&2
    tail -n 20 preview.log >&2 || true
    exit 1
  fi
fi

# ── 4. Resolve the actual streamlit python pid ─────────────────────────
STREAMLIT_PID="$(ss -ltnp 2>/dev/null | grep -E ":${PORT}\b" | grep -oE 'pid=[0-9]+' | head -1 | cut -d= -f2 || true)"
HEALTH="$(curl -fsS "http://${HOST}:${PORT}/_stcore/health" 2>/dev/null | tr -d '\n' || echo unknown)"

# ── 5. Report ───────────────────────────────────────────────────────────
echo ""
echo "── OpenRadar preview ──"
echo "  branch : $BRANCH"
echo "  commit : $COMMIT_LONG"
echo "  port   : $PORT"
echo "  host   : $HOST"
echo "  pid    : ${STREAMLIT_PID:-?}"
echo "  health : $HEALTH"
echo "  log    : $(pwd)/preview.log"
echo ""
echo "── Mac SSH tunnel (run on your workstation) ──"
echo "  ssh -N -L ${PORT}:127.0.0.1:${PORT} opencode@srv1351019"
echo ""
echo "── Browser URL (after tunnel) ──"
echo "  http://127.0.0.1:${PORT}"
echo "  http://127.0.0.1:${PORT}/?section=learning"
echo ""
echo "── Stop with ──"
echo "  bash scripts/stop-preview.sh"