import type { CSSProperties } from "react";

/**
 * Build an inline style object that consumes only semantic tokens.
 * Use this when a component needs an inline style (e.g. for SVG fills)
 * and must respect the active accent.
 */
export const t = {
  chassis: { backgroundColor: "var(--surface-chassis)" },
  recessed: { backgroundColor: "var(--surface-recessed)" },
  raised: { backgroundColor: "var(--surface-raised)" },
  glass: { backgroundColor: "var(--surface-glass-deep)" },
  trim: { borderColor: "var(--edge-trim)" },
  bronze: { borderColor: "var(--edge-bronze)" },
  signalFill: { fill: "var(--signal-primary)" } as CSSProperties,
  signalStroke: { stroke: "var(--signal-primary)" } as CSSProperties,
  phosphor: { fill: "var(--accent-phosphor)" } as CSSProperties,
  phosphorStroke: { stroke: "var(--accent-phosphor)" } as CSSProperties,
  textData: { color: "var(--text-data)" },
} as const;