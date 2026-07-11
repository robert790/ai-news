"use client";

import { useAccent } from "@/lib/accent-context";
import { ACCENT_PRESETS, type AccentName } from "@/lib/accent";

function angleFor(i: number): number {
  // Start at -90° (top) and rotate clockwise.
  return -90 + (360 / ACCENT_PRESETS.length) * i;
}

/**
 * ThemeDial — physical rotary control that selects the accent preset.
 *
 * Rendered as a 5-position rotary. Each position is a real <button>
 * with aria-pressed. Keyboard:
 *   - Tab into the dial focuses the currently-selected position
 *   - Arrow keys rotate (Left/Up = previous, Right/Down = next)
 *   - Home/End jump to first/last
 *
 * Visual: a circular metal bezel with a phosphor pointer indicating
 * the active position. Pure SVG; no canvas.
 */
export function ThemeDial() {
  const { accent, setAccent } = useAccent();
  const idx = ACCENT_PRESETS.findIndex((p) => p.name === accent);
  const safeIdx = idx === -1 ? 0 : idx;

  const onKey = (e: React.KeyboardEvent<HTMLDivElement>) => {
    let next = safeIdx;
    let handled = true;
    switch (e.key) {
      case "ArrowRight":
      case "ArrowDown":
        next = (safeIdx + 1) % ACCENT_PRESETS.length;
        break;
      case "ArrowLeft":
      case "ArrowUp":
        next = (safeIdx - 1 + ACCENT_PRESETS.length) % ACCENT_PRESETS.length;
        break;
      case "Home":
        next = 0;
        break;
      case "End":
        next = ACCENT_PRESETS.length - 1;
        break;
      default:
        handled = false;
    }
    if (handled) {
      e.preventDefault();
      setAccent(ACCENT_PRESETS[next].name as AccentName);
    }
  };

  return (
    <div
      role="radiogroup"
      aria-label="Accent preset — ThemeDial"
      onKeyDown={onKey}
      className="inline-flex items-center gap-3"
    >
      <DialFace current={safeIdx} />
      <div className="flex flex-col gap-1">
        <div className="text-label">ThemeDial</div>
        <div
          className="text-data"
          style={{ color: "var(--text-primary)", fontSize: "13px" }}
        >
          {ACCENT_PRESETS[safeIdx].label}
        </div>
        <div
          className="text-data"
          style={{ color: "var(--text-muted)", fontSize: "11px" }}
        >
          {ACCENT_PRESETS[safeIdx].description}
        </div>
      </div>
      {/* Hidden real <button>s for AT and click-only fallback. */}
      <div className="sr-only">
        {ACCENT_PRESETS.map((p) => (
          <button
            key={p.name}
            type="button"
            aria-pressed={p.name === accent}
            aria-label={`Set accent to ${p.label}`}
            onClick={() => setAccent(p.name)}
          >
            {p.label}
          </button>
        ))}
      </div>
    </div>
  );
}

function DialFace({ current }: { current: number }) {
  const size = 88;
  const r = size / 2 - 6;
  const cx = size / 2;
  const cy = size / 2;

  // Pointer rotation
  const angle = angleFor(current);
  const rad = (angle * Math.PI) / 180;
  const px = cx + (r - 14) * Math.cos(rad);
  const py = cy + (r - 14) * Math.sin(rad);

  return (
    <svg
      width={size}
      height={size}
      viewBox={`0 0 ${size} ${size}`}
      role="presentation"
      data-decorative="true"
      aria-hidden="true"
      style={{ filter: "drop-shadow(0 4px 8px rgba(0,0,0,0.4))" }}
    >
      {/* Outer bezel ring */}
      <defs>
        <radialGradient id="dialBezel" cx="50%" cy="35%" r="65%">
          <stop offset="0%" stopColor="var(--edge-trim-bright)" />
          <stop offset="55%" stopColor="var(--edge-trim)" />
          <stop offset="100%" stopColor="#0d1013" />
        </radialGradient>
        <radialGradient id="dialFace" cx="50%" cy="40%" r="60%">
          <stop offset="0%" stopColor="var(--surface-raised)" />
          <stop offset="100%" stopColor="var(--surface-chassis-deep)" />
        </radialGradient>
      </defs>
      <circle cx={cx} cy={cy} r={r + 4} fill="url(#dialBezel)" />
      {/* Knurled ticks around the bezel */}
      {Array.from({ length: 36 }).map((_, i) => {
        const a = (i * 10 * Math.PI) / 180;
        const x1 = cx + (r + 2) * Math.cos(a);
        const y1 = cy + (r + 2) * Math.sin(a);
        const x2 = cx + (r + 5) * Math.cos(a);
        const y2 = cy + (r + 5) * Math.sin(a);
        return (
          <line
            key={i}
            x1={x1}
            y1={y1}
            x2={x2}
            y2={y2}
            stroke="var(--edge-trim-bright)"
            strokeWidth="0.6"
            opacity={i % 3 === 0 ? 0.7 : 0.35}
          />
        );
      })}
      <circle cx={cx} cy={cy} r={r - 6} fill="url(#dialFace)" />
      <circle
        cx={cx}
        cy={cy}
        r={r - 6}
        fill="none"
        stroke="rgba(0,0,0,0.6)"
        strokeWidth="1"
      />
      {/* Active position dot (where the pointer lands) */}
      <circle
        cx={px}
        cy={py}
        r={4}
        fill="var(--accent-phosphor)"
        style={{ filter: "drop-shadow(0 0 6px var(--accent-phosphor-soft))" }}
      />
      {/* Center hub */}
      <circle cx={cx} cy={cy} r={5} fill="var(--edge-trim-bright)" />
      <circle cx={cx} cy={cy} r={2.5} fill="#0c0f11" />
      {/* Labels for each preset position */}
      {ACCENT_PRESETS.map((p, i) => {
        const a = angleFor(i);
        const arad = (a * Math.PI) / 180;
        const lx = cx + (r - 22) * Math.cos(arad);
        const ly = cy + (r - 22) * Math.sin(arad);
        return (
          <text
            key={p.name}
            x={lx}
            y={ly}
            textAnchor="middle"
            dominantBaseline="middle"
            fill={i === current ? "var(--text-primary)" : "var(--text-muted)"}
            fontFamily="var(--font-mono)"
            fontSize="8"
            letterSpacing="0.5"
          >
            {p.tag}
          </text>
        );
      })}
    </svg>
  );
}