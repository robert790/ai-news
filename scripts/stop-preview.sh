#!/usr/bin/env bash
# Stop the OpenRadar PR preview server on the standard port (8780).
#
# Only touches processes whose cmdline literally contains
# 'streamlit run app.py'. Hermes on 9119 is never matched.
# See docs/WORKFLOW.md for the convention.

set -euo pipefail

PORT="${PORT:-8780}"
APP_FILE="app.py"

# Find every python process whose full cmdline includes both
# "streamlit run <APP_FILE>" and "--server.port <PORT>".
mapfile -t TARGETS < <(
  ps -eo pid=,args= 2>/dev/null \
    | awk -v app="$APP_FILE" -v port="$PORT" '
        $0 ~ "streamlit run " app " " && $0 ~ "--server.port " port "|" "--server.port " port "$" {
          print $1
        }
      ' \
    | tr -d ' '
)

if [[ "${#TARGETS[@]}" -eq 0 ]]; then
  echo "✓ no OpenRadar preview server running on $PORT"
  ss -ltnp 2>/dev/null | grep -E ":${PORT}\b" || true
  exit 0
fi

echo "→ stopping ${#TARGETS[@]} OpenRadar preview process(es) on $PORT:"
for pid in "${TARGETS[@]}"; do
  echo "  · pid $pid"
  kill "$pid" 2>/dev/null || true
done

# Wait up to 5s for the port to free up.
for _ in $(seq 1 10); do
  sleep 0.5
  if ! ss -ltnp 2>/dev/null | grep -E ":${PORT}\b" >/dev/null; then
    break
  fi
done

# Force-kill anything still hanging on.
if ss -ltnp 2>/dev/null | grep -E ":${PORT}\b" >/dev/null; then
  echo "→ force-killing remaining listeners on $PORT"
  for pid in "${TARGETS[@]}"; do
    kill -9 "$pid" 2>/dev/null || true
  done
  sleep 1
fi

echo ""
echo "── After cleanup ──"
echo "  port $PORT listeners:"
ss -ltnp 2>/dev/null | grep -E ":${PORT}\b" || echo "    (none)"
echo "  Hermes port 9119 listeners (must stay alive):"
ss -ltnp 2>/dev/null | grep -E ":9119\b" || echo "    (none — Hermes itself is offline)"