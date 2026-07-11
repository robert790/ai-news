/**
 * OpenRadar Web V2 — Accent Preset Registry
 *
 * The five accent presets swap signal/phosphor colors only.
 * The chassis, glass, edges, typography, spacing, and motion
 * remain identical. This file is the single source of truth for
 * ThemeDial options.
 *
 * Adding an accent: extend the union and add an entry here AND
 * the matching `[data-accent="x"]` block in tokens.css.
 */

export type AccentName = "green" | "amber" | "cyan" | "red" | "violet";

export interface AccentPreset {
  name: AccentName;
  label: string;
  /** Short mono tag for the dial face (e.g. "GRN"). */
  tag: string;
  /** Human-readable description used by the ThemeDial tooltip. */
  description: string;
}

export const ACCENT_PRESETS: ReadonlyArray<AccentPreset> = [
  {
    name: "green",
    label: "Phosphor Green",
    tag: "GRN",
    description: "Classic terminal phosphor — calm, neutral, default.",
  },
  {
    name: "amber",
    label: "Amber",
    tag: "AMB",
    description: "Warm amber — vintage instrument, lower eye fatigue at night.",
  },
  {
    name: "cyan",
    label: "Cyan",
    tag: "CYN",
    description: "Cool cyan — analytical, ocean-instrument feel.",
  },
  {
    name: "red",
    label: "Alert Red",
    tag: "RED",
    description: "High-attention red — broadcast / live-event surfaces.",
  },
  {
    name: "violet",
    label: "Violet",
    tag: "VLT",
    description: "Violet — exploratory, learn-mode surfaces.",
  },
] as const;

export const DEFAULT_ACCENT: AccentName = "green";

export const ACCENT_NAMES: ReadonlyArray<AccentName> = ACCENT_PRESETS.map(
  (p) => p.name,
);