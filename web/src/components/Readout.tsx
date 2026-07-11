export interface ReadoutProps {
  label: string;
  value: string;
  /** Optional unit, e.g. "ms", "%", "ops/s". */
  unit?: string;
  /** Tone — "primary" uses phosphor, "neutral" uses data color. */
  tone?: "phosphor" | "neutral";
}

export function Readout({ label, value, unit, tone = "phosphor" }: ReadoutProps) {
  return (
    <div className="flex flex-col">
      <span
        className="text-label"
        style={{ fontSize: "9px", letterSpacing: "0.08em" }}
      >
        {label}
      </span>
      <span
        className={tone === "phosphor" ? "ort-readout" : "text-data"}
        style={{ fontSize: "14px" }}
      >
        {value}
        {unit && (
          <span style={{ color: "var(--text-muted)", marginLeft: 4 }}>
            {unit}
          </span>
        )}
      </span>
    </div>
  );
}