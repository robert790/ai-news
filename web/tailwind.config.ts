import type { Config } from "tailwindcss";

/**
 * OpenRadar Web V2 — Tailwind config.
 *
 * IMPORTANT: Tailwind utility classes are intentionally thin wrappers here.
 * The chassis, glass, bronze-trim, phosphor, and accent tokens live in
 * CSS custom properties (src/styles/tokens.css) so themes change by
 * swapping variables on the root element — not by repainting components.
 *
 * Tailwind is used for layout primitives, spacing, and responsive helpers.
 */
const config: Config = {
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      // Map a tiny set of utility classes to semantic CSS variables.
      // Components should consume `bg-chassis`, `text-text`, `border-trim`,
      // etc. rather than raw colors.
      colors: {
        chassis: "var(--surface-chassis)",
        "chassis-deep": "var(--surface-chassis-deep)",
        "chassis-recessed": "var(--surface-recessed)",
        "chassis-raised": "var(--surface-raised)",
        glass: "var(--surface-glass)",
        "glass-deep": "var(--surface-glass-deep)",
        trim: "var(--edge-trim)",
        "trim-bright": "var(--edge-trim-bright)",
        bronze: "var(--edge-bronze)",
        "bronze-bright": "var(--edge-bronze-bright)",
        text: "var(--text-primary)",
        "text-dim": "var(--text-secondary)",
        "text-muted": "var(--text-muted)",
        "text-data": "var(--text-data)",
        phosphor: "var(--accent-phosphor)",
        "phosphor-soft": "var(--accent-phosphor-soft)",
        signal: "var(--signal-primary)",
        "signal-soft": "var(--signal-soft)",
        focus: "var(--state-focus)",
        success: "var(--state-success)",
        warning: "var(--state-warning)",
        danger: "var(--state-danger)",
        info: "var(--state-info)",
        neutral: "var(--state-neutral)",
      },
      borderRadius: {
        chassis: "var(--radius-chassis)",
        panel: "var(--radius-panel)",
        control: "var(--radius-control)",
        "control-sm": "var(--radius-control-sm)",
        pill: "var(--radius-pill)",
      },
      boxShadow: {
        chassis: "var(--shadow-chassis)",
        raised: "var(--shadow-raised)",
        recessed: "var(--shadow-recessed)",
        glass: "var(--shadow-glass)",
        trim: "var(--shadow-trim)",
        focus: "var(--shadow-focus)",
        signal: "var(--shadow-signal)",
      },
      fontFamily: {
        sans: ["var(--font-sans)"],
        mono: ["var(--font-mono)"],
      },
      transitionDuration: {
        fast: "var(--motion-fast)",
        base: "var(--motion-base)",
        slow: "var(--motion-slow)",
      },
    },
  },
  plugins: [],
};

export default config;