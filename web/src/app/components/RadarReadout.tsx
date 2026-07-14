import * as React from "react";

/**
 * Telemetry readout chip — the four corner labels around the radar
 * (RNG, BRG, SWP, CHN).
 *
 * DOM contract:
 *   <div class="radar-readout radar-readout--{corner}">
 *     <span>{label}</span>
 *     <strong>{value}</strong>
 *   </div>
 */
export function RadarReadout({
  corner,
  label,
  value,
}: {
  corner: "nw" | "ne" | "sw" | "se";
  label: string;
  value: string;
}): JSX.Element {
  return (
    <div className={`radar-readout radar-readout--${corner}`}>
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}