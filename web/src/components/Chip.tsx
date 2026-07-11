import type { ReactNode } from "react";

export interface ChipProps {
  children: ReactNode;
  /** Tone — "signal" lights the chip with the active accent; "neutral" stays dim. */
  tone?: "signal" | "neutral";
}

export function Chip({ children, tone = "neutral" }: ChipProps) {
  if (tone === "signal") {
    return (
      <span
        className="ort-chip"
        style={{
          color: "var(--signal-primary)",
          borderColor: "var(--signal-edge)",
          background: "var(--signal-soft)",
        }}
      >
        {children}
      </span>
    );
  }
  return <span className="ort-chip">{children}</span>;
}