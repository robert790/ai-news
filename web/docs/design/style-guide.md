# OpenRadar Style Guide

This guide describes the **visual primitives** that will be promoted into reusable components in stage 1b. Each entry maps a current `spike.css` class to the component it should become, the tokens it consumes, and the freeze screenshot that proves it.

The freeze commit (`69a4ba2`) is the source of truth; the style guide is documentation, not authority.

## Layout primitives

| Primitive | Current class | Composition token | Notes |
| --- | --- | --- | --- |
| Page shell | `.page-shell` | `--or-shell-pad`, `--or-shell-pad-mobile` | Outer flex container that centers the chassis |
| Chassis | `.machine` | `--or-shadow-machine`, `--or-machine-pad`, `--or-machine-max` | Bronze-trimmed chassis with bolt corners and rim seams |
| Bolt corner | `.bolt` + `.machine-bolt--*`, `.hero-bolt--*` | none (literal) | Decorative; positioned absolutely on chassis and hero |
| Section | (none — divs) | none | No component yet; the freeze uses raw `<section>` blocks |

## Visual primitives

| Primitive | Current class | Token group | Notes |
| --- | --- | --- | --- |
| Bronze rim seam | `.machine::before/::after` | `--or-rim-*` | Top/bottom bronze seam; pure decoration |
| Brand scope | `.brand-scope`, `.mini-scope` | none (literal) | Phosphor scope with sweep + crosshairs |
| Dial | `.dial` | none (literal) | Conic-gradient knob |
| Pulse bar | `.pulse` + `::after` | `--accent`, `--accent-deep-300` | Animated EKG-style accent bar |
| Status icon disc | `.status-icon` | none | 27px circular ring holding one glyph |

## Composition primitives

| Primitive | Current class | Token group | Notes |
| --- | --- | --- | --- |
| Top deck | `.top-deck` | none | 3-column nav strip |
| Hero deck | `.hero-deck` | none | Hero panel with grips + bolts |
| Radar rig | `.radar-rig` + `.radar-bezel` + `.radar-glass` + `.radar-grid` + `.radar-beam` + `.radar-origin` + `.radar-bearing` | `--accent-deep-*`, `--or-sweep-duration` | The center of the console |
| Radar readout | `.radar-readout` + `--nw/--ne/--sw/--se` | none | Corner clip-path readout chip |
| Status rail | `.status-rail` | none | 5-up grid (2-up on mobile) |
| Module card | `.module` + `.module-head` + `.module-body` + `.module-code` | none | Bronze-trimmed card with header + body |
| Lower bank | `.lower-bank` + `.signal-panel`, `.updates-panel`, `.health-panel` | none | 3-column secondary deck |
| Footer deck | `.footer-deck` + `.footer-mark` + `dl`, `form`, `.legal` | none | Bottom strip with mark, metadata, subscribe, legal |

## Component extraction plan (stage 1b)

The next commit will introduce `web/src/app/components/` with one component per primitive above. Each component must:

1. Render the **exact same DOM** the freeze produces (no extra wrappers, no missing children).
2. Use only `--or-*` tokens from `tokens.css` plus the `--accent*` family.
3. Be importable without React context, providers, or side effects.
4. Pass `aria-*` and `role` attributes through unchanged.

## What this guide does NOT cover

- Streamlit surfaces (out of scope for the home/system industrialization pass).
- The rejected MiniMax spike styling on `feature/web-v2-chassis-rebuild-spike`. Do not reuse anything from that branch.
- New color, type, or motion tokens. If a value is missing from `tokens.css`, the freeze probably does not have it.