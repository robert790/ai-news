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
              <radialGradient id="radarField">
                <stop offset="0" stopColor="#1b351b" stopOpacity=".72" />
                <stop offset=".68" stopColor="#071208" stopOpacity=".85" />
                <stop offset="1" stopColor="#010402" />
              </radialGradient>
              <linearGradient id="beam" x1="0" x2="1">
                <stop stopColor="#baff71" stopOpacity=".04" />
                <stop offset="1" stopColor="#baff71" stopOpacity=".78" />
              </linearGradient>
              <radialGradient id="blip">
                <stop stopColor="#e5ffae" />
                <stop offset=".45" stopColor="#9de95f" />
                <stop offset="1" stopColor="#79c84c" stopOpacity="0" />
              </radialGradient>
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
              <circle key={index} cx={cx} cy={cy} r="4" fill="url(#blip)" />
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