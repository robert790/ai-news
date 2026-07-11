export interface StatusLampProps {
  /** Visual state. Drives color via semantic token only. */
  state?: "ok" | "warn" | "err" | "idle";
  /** Accessible label. If omitted, the lamp is decorative. */
  label?: string;
  /** Pulse the lamp (live indicator). Default false. */
  pulse?: boolean;
}

export function StatusLamp({ state = "ok", label, pulse = false }: StatusLampProps) {
  const cls =
    state === "ok"
      ? "ort-lamp ort-lamp--ok"
      : state === "warn"
        ? "ort-lamp ort-lamp--warn"
        : state === "err"
          ? "ort-lamp ort-lamp--err"
          : "ort-lamp ort-lamp--idle";

  const dot = (
    <span
      className={cls}
      style={
        pulse
          ? { animation: "ort-lamp-pulse 1.6s ease-in-out infinite" }
          : undefined
      }
      aria-hidden={label ? undefined : true}
    />
  );

  if (label) {
    return (
      <span className="inline-flex items-center gap-2 text-data" style={{ fontSize: "11px" }}>
        {dot}
        <span style={{ color: "var(--text-secondary)" }}>{label}</span>
      </span>
    );
  }
  return dot;
}