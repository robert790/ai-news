import * as React from "react";
import { RadarReadout } from "./RadarReadout";

/**
 * The radar rig: four corner readouts around a circular CRT-style
 * radar. SVG coordinates and blip positions are taken verbatim
 * from the freeze.
 */
const BLIPS: ReadonlyArray<readonly [number, number]> = [
  [69, 55],
  [132, 73],
  [150, 116],
  [117, 145],
  [62, 132],
  [47, 92],
];

export function Radar({
  readouts = [
    { corner: "nw" as const, label: "RNG", value: "200" },
    { corner: "ne" as const, label: "BRG", value: "315°" },
    { corner: "sw" as const, label: "SWP", value: "04.2s" },
    { corner: "se" as const, label: "CHN", value: "A" },
  ],
  blips = BLIPS,
  ariaLabel = "OpenRadar signal display",
  svgLabel = "Radar showing six current signals",
}: {
  readouts?: ReadonlyArray<{ corner: "nw" | "ne" | "sw" | "se"; label: string; value: string }>;
  blips?: ReadonlyArray<readonly [number, number]>;
  ariaLabel?: string;
  svgLabel?: string;
}): JSX.Element {
  return (
    <div className="radar-rig" aria-label={ariaLabel}>
      {readouts.map((r) => (
        <RadarReadout key={r.corner} corner={r.corner} label={r.label} value={r.value} />
      ))}
      <div className="radar-bezel">
        <div className="radar-glass">
          <svg viewBox="0 0 200 200" role="img" aria-label={svgLabel}>
            <defs>
              {/*
                The radar field gradient is dark-green phosphor —
                a material layer that stays frozen across skins. The
                beam and blip gradients read --accent-beam-* and
                --accent-blip-* / --accent-deep-* through inline
                style so they re-skin with the active data-skin.
              */}
              <radialGradient id="radarField">
                <stop offset="0" stopColor="#1b351b" stopOpacity=".72" />
                <stop offset=".68" stopColor="#071208" stopOpacity=".85" />
                <stop offset="1" stopColor="#010402" />
              </radialGradient>
              <linearGradient id="beam" x1="0" x2="1">
                <stop style={{ stopColor: "var(--accent-beam-100)" }} stopOpacity=".04" />
                <stop offset="1" style={{ stopColor: "var(--accent-beam-200)" }} stopOpacity=".78" />
              </linearGradient>
              <radialGradient id="blip">
                <stop style={{ stopColor: "var(--accent-blip-100)" }} />
                <stop offset=".45" style={{ stopColor: "var(--accent-deep-400)" }} />
                <stop offset="1" style={{ stopColor: "var(--accent-deep-700)" }} stopOpacity="0" />
              </radialGradient>
              <filter id="blipGlow" x="-250%" y="-250%" width="600%" height="600%">
                <feGaussianBlur stdDeviation="1.4" result="blur" />
                <feMerge>
                  <feMergeNode in="blur" />
                  <feMergeNode in="SourceGraphic" />
                </feMerge>
              </filter>
            </defs>
            <circle cx="100" cy="100" r="98" fill="url(#radarField)" />
            {[24, 43, 62, 81].map((r) => (
              <circle key={r} cx="100" cy="100" r={r} className="radar-grid" />
            ))}
            <path d="M4 100H196M100 4V196" className="radar-grid" />
            <path
              d="M100 100L184 44A101 101 0 0 1 197 77Z"
              fill="url(#beam)"
              className="radar-beam"
            />
            <circle cx="100" cy="100" r="2.5" className="radar-origin" />
            {blips.map(([cx, cy], index) => (
              <g
                key={index}
                className="radar-blip"
                style={{ "--blip-delay": `${index * -0.71}s` } as React.CSSProperties}
              >
                <circle cx={cx} cy={cy} r="5.5" fill="url(#blip)" className="radar-blip__afterglow" />
                <circle cx={cx} cy={cy} r="1.65" className="radar-blip__core" filter="url(#blipGlow)" />
              </g>
            ))}
            <g className="radar-bearing">
              <text x="96" y="12">000</text>
              <text x="176" y="104">090</text>
              <text x="94" y="193">180</text>
              <text x="8" y="104">270</text>
            </g>
          </svg>
        </div>
      </div>
    </div>
  );
}