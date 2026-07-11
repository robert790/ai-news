export interface DataBadgeProps {
  /** Big mono number, the readout. */
  value: string;
  /** Small label above. */
  label: string;
  /** Optional trend glyph: "up" / "down" / "flat". */
  trend?: "up" | "down" | "flat";
}

export function DataBadge({ value, label, trend }: DataBadgeProps) {
  const trendGlyph =
    trend === "up" ? "▲" : trend === "down" ? "▼" : trend === "flat" ? "—" : null;
  const trendColor =
    trend === "up"
      ? "var(--state-success)"
      : trend === "down"
        ? "var(--state-danger)"
        : "var(--text-muted)";
  return (
    <div
      className="ort-badge"
      style={{
        flexDirection: "column",
        alignItems: "flex-start",
        padding: "8px 10px",
        gap: 2,
      }}
    >
      <span className="text-label" style={{ fontSize: "9px" }}>
        {label}
      </span>
      <span
        className="ort-readout"
        style={{ fontSize: "16px", display: "inline-flex", gap: 6, alignItems: "baseline" }}
      >
        {value}
        {trendGlyph && (
          <span style={{ color: trendColor, fontSize: "10px" }}>{trendGlyph}</span>
        )}
      </span>
    </div>
  );
}