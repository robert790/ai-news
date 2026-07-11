# OpenRadar Design Tokens

This document is the human-readable mirror of `web/src/app/styles/tokens.css`. Every value listed here is extracted verbatim from the **accepted Sol Home baseline** (freeze commit `69a4ba2`, file `web/src/styles/spike.css`). Do not introduce new tokens — only lift values that already exist on the frozen Home.

The Home freeze is the visual source of truth; tokens exist to let other surfaces reuse the same material language, not to drift from it.

---

## Naming

All tokens use the `--or-` (OpenRadar) prefix to avoid collisions with Tailwind / shadcn defaults and to make "OpenRadar-specific material" obvious at the call site.

| Group | Prefix | Role |
| --- | --- | --- |
| Material — chassis | `--or-steel-*` | Base palette for machine gradients and inner panels |
| Material — trim | `--or-bronze-*` | Edges, bolt rims, lit borders |
| Material — rim | `--or-rim-*` | Warm bronze seam at top/bottom of the machine |
| Type — cream | `--or-cream-*` | Primary text, headlines, lede |
| Type — warm | `--or-warm-*` | Dim text, telemetry, footer dt |
| Type — bronze | `--or-bronze-num-*` | Bronze numerals (status rail, kit numbers) |
| Accent | `--accent*` | Skin-switchable; see below |
| Accent — deep | `--accent-deep-*` | Glow / grid / nav glow variations |
| Accent — glow | `--accent-glow-*` | Translucent halos |
| Type stacks | `--or-font-*` | Mono + display families |
| Motion | `--or-sweep-*`, `--or-ease` | Radar sweep period and easing |
| Dimensions | `--or-shell-*`, `--or-machine-*` | Page shell and chassis geometry |
| Strokes / radii / shadows | `--or-stroke-*`, `--or-radius-*`, `--or-shadow-*` | Borderline + lift values |

## Accent presets

`tokens.css` defines one default accent (`Sol phosphor green`). The five approved presets are wired through the `[data-skin="…"]` selectors in `globals.css`:

| Skin | Source color | Use |
| --- | --- | --- |
| `green` (default) | `#a8ec62` | Accepted Home freeze |
| `amber` | `#f3b95a` | Warm-toned cockpit variant |
| `cyan` | `#62c8ec` | Cool diagnostic variant |
| `red` | `#ec6262` | High-contrast alarm variant |
| `violet` | `#b48aff` | Editorial / signal variant |

To re-skin a chassis, set `data-skin="amber"` (or any of the above) on the `<html>`, `<body>`, or any ancestor of `.machine`. Components must consume only `--accent`, `--accent-strong`, `--accent-rgb`, and the `--accent-deep-*` series — never the literal preset hex.

## When to add a new token

New tokens require a reviewed, baseline-backed need and must preserve the accepted material system. The freeze is the default reference; before adding a token, confirm the absence is unintentional, propose the new value with a freeze reference, and capture an updated visual baseline.

## When to add a new accent preset

Add it as a new `[data-skin="…"]` block in `globals.css` (same shape as the five listed above) and document it here. Do not introduce a parallel token file. The five approved preset names are `green`, `amber`, `cyan`, `red`, `violet`. Do not introduce alternate spellings (e.g. `sol`, `magenta`, `copper`).