import type { ReactNode } from "react";

/**
 * SignalRow — single line of instrument-style telemetry.
 * Icon + label + value + optional state.
 */
export interface SignalRowProps {
  icon?: ReactNode;
  label: string;
  value: ReactNode;
  state?: "ok" | "warn" | "err" | "idle";
}

export function SignalRow({ icon, label, value, state = "ok" }: SignalRowProps) {
  const lampCls =
    state === "ok"
      ? "ort-lamp ort-lamp--ok"
      : state === "warn"
        ? "ort-lamp ort-lamp--warn"
        : state === "err"
          ? "ort-lamp ort-lamp--err"
          : "ort-lamp ort-lamp--idle";
  return (
    <div className="ort-list-item">
      <span className={lampCls} aria-hidden="true" />
      {icon && (
        <span aria-hidden="true" style={{ color: "var(--text-muted)" }}>
          {icon}
        </span>
      )}
      <span className="text-data" style={{ fontSize: "11px", color: "var(--text-secondary)" }}>
        {label}
      </span>
      <span className="ml-auto text-data" style={{ fontSize: "12px" }}>
        {value}
      </span>
    </div>
  );
}