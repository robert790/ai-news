import { useId } from "react";

export interface RadarProps {
  /** Heading angle in degrees (0 = north, clockwise). Default 45. */
  heading?: number;
  /** Range rings count. Default 5. */
  rings?: number;
  /** Number of blip dots to render. */
  blips?: number;
  /** Diameter in px. Defaults to fill container. */
  size?: number;
  /** Readout corners — small label/value pairs in each cardinal corner. */
  readouts?: { label: string; value: string }[];
  /** Disable sweep animation (reduced-motion or off-mode). */
  animate?: boolean;
}

/**
 * Radar — the defining instrument.
 * Pure SVG, no canvas. Concentric range rings, cardinal ticks,
 * a phosphor sweep wedge, and scattered blip dots.
 *
 * Server-renderable. The sweep keyframe lives in tailwind.css
 * (.ort-sweep-rotate) so this stays usable from RSC.
 */
export function Radar({
  heading = 45,
  rings = 5,
  blips = 6,
  size,
  readouts = [
    { label: "RNG", value: "024" },
    { label: "BRG", value: "045" },
    { label: "SWP", value: "4S" },
    { label: "CHN", value: "07" },
  ],
  animate = true,
}: RadarProps) {
  const id = useId().replace(/:/g, "");
  const cx = 100;
  const cy = 100;
  const r = 90;

  // Deterministic blip positions (seeded pseudo-random for SSR consistency).
  const blipPositions = Array.from({ length: blips }).map((_, i) => {
    const a = ((i * 67 + 23) % 360) * (Math.PI / 180);
    const rr = ((i * 13 + 17) % 90) + 8;
    return {
      x: cx + rr * Math.cos(a),
      y: cy + rr * Math.sin(a),
      r: 1.5 + (i % 3) * 0.4,
    };
  });

  return (
    <div
      className="ort-glass relative"
      style={{
        width: size ?? "100%",
        aspectRatio: "1 / 1",
        maxWidth: size ?? 360,
        margin: "0 auto",
      }}
      role="img"
      aria-label={`Radar instrument. Heading ${heading} degrees. ${blips} active contacts.`}
    >
      <svg
        viewBox="0 0 200 200"
        width="100%"
        height="100%"
        data-decorative="true"
        aria-hidden="true"
      >
        <defs>
          <radialGradient id={`bg-${id}`} cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="rgba(120,160,170,0.06)" />
            <stop offset="80%" stopColor="rgba(0,0,0,0)" />
          </radialGradient>
          <mask id={`sweepmask-${id}`}>
            <rect width="200" height="200" fill="black" />
            <g>
              <path
                d={`M 100 100 L ${cx + r} 100 A ${r} ${r} 0 0 1 ${
                  cx + r * Math.cos(-Math.PI / 6)
                } ${cy + r * Math.sin(-Math.PI / 6)} Z`}
                fill="white"
                className={animate ? "ort-sweep-rotate" : ""}
              />
            </g>
          </mask>
        </defs>

        <circle cx={cx} cy={cy} r={r} fill={`url(#bg-${id})`} />

        {Array.from({ length: rings }).map((_, i) => {
          const rr = (r * (i + 1)) / rings;
          return (
            <circle
              key={i}
              cx={cx}
              cy={cy}
              r={rr}
              fill="none"
              stroke="var(--signal-primary)"
              strokeOpacity={0.18 + (i / rings) * 0.15}
              strokeWidth="0.5"
            />
          );
        })}

        {[0, 90, 180, 270].map((deg) => {
          const arad = (deg * Math.PI) / 180;
          const x1 = cx + (r - 4) * Math.cos(arad);
          const y1 = cy + (r - 4) * Math.sin(arad);
          const x2 = cx + r * Math.cos(arad);
          const y2 = cy + r * Math.sin(arad);
          return (
            <line
              key={deg}
              x1={x1}
              y1={y1}
              x2={x2}
              y2={y2}
              stroke="var(--signal-primary)"
              strokeOpacity="0.55"
              strokeWidth="1"
            />
          );
        })}

        {Array.from({ length: 24 }).map((_, i) => {
          if (i % 6 === 0) return null;
          const deg = i * 15;
          const arad = (deg * Math.PI) / 180;
          const x1 = cx + (r - 2) * Math.cos(arad);
          const y1 = cy + (r - 2) * Math.sin(arad);
          const x2 = cx + r * Math.cos(arad);
          const y2 = cy + r * Math.sin(arad);
          return (
            <line
              key={`min-${i}`}
              x1={x1}
              y1={y1}
              x2={x2}
              y2={y2}
              stroke="var(--signal-primary)"
              strokeOpacity="0.3"
              strokeWidth="0.5"
            />
          );
        })}

        <line
          x1={cx - r}
          y1={cy}
          x2={cx + r}
          y2={cy}
          stroke="var(--signal-primary)"
          strokeOpacity="0.08"
          strokeWidth="0.5"
        />
        <line
          x1={cx}
          y1={cy - r}
          x2={cy}
          y2={cy + r}
          stroke="var(--signal-primary)"
          strokeOpacity="0.08"
          strokeWidth="0.5"
        />

        {animate && (
          <circle
            cx={cx}
            cy={cy}
            r={r}
            fill="var(--accent-phosphor)"
            opacity="0.18"
            mask={`url(#sweepmask-${id})`}
          />
        )}
        <g>
          <line
            x1={cx}
            y1={cy}
            x2={cx + (r - 4) * Math.cos((heading * Math.PI) / 180)}
            y2={cy + (r - 4) * Math.sin((heading * Math.PI) / 180)}
            stroke="var(--accent-phosphor)"
            strokeWidth="1.4"
            opacity="0.85"
          />
        </g>

        {blipPositions.map((b, i) => (
          <circle
            key={i}
            cx={b.x}
            cy={b.y}
            r={b.r}
            fill="var(--accent-phosphor)"
            style={{
              filter: "drop-shadow(0 0 4px var(--accent-phosphor-soft))",
            }}
          />
        ))}

        <circle cx={cx} cy={cy} r={3.5} fill="var(--edge-trim-bright)" />
        <circle cx={cx} cy={cy} r={1.6} fill="#0c0f11" />

        <circle
          cx={cx}
          cy={cy}
          r={r + 1}
          fill="none"
          stroke="var(--edge-trim-bright)"
          strokeWidth="2"
          opacity="0.7"
        />
      </svg>

      <div
        className="absolute inset-0 pointer-events-none text-data"
        style={{ fontSize: "9px" }}
      >
        <div className="absolute top-1 left-1.5 leading-tight">
          <div style={{ color: "var(--text-muted)" }}>{readouts[0].label}</div>
          <div className="ort-readout">{readouts[0].value}</div>
        </div>
        <div className="absolute top-1 right-1.5 leading-tight text-right">
          <div style={{ color: "var(--text-muted)" }}>{readouts[1].label}</div>
          <div className="ort-readout">{readouts[1].value}</div>
        </div>
        <div className="absolute bottom-1 left-1.5 leading-tight">
          <div style={{ color: "var(--text-muted)" }}>{readouts[2].label}</div>
          <div className="ort-readout">{readouts[2].value}</div>
        </div>
        <div className="absolute bottom-1 right-1.5 leading-tight text-right">
          <div style={{ color: "var(--text-muted)" }}>{readouts[3].label}</div>
          <div className="ort-readout">{readouts[3].value}</div>
        </div>
      </div>
    </div>
  );
}