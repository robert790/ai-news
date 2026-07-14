import * as React from "react";

/**
 * Circular phosphor scope.
 *
 * Used as the brand mark (left of the wordmark) and as the mini
 * footer mark (left of the footer tagline). The visual difference
 * is purely the wrapping class name: `brand-scope` for the
 * desktop brand, `mini-scope` for the footer.
 *
 * The internal sweep tick is animated via the .radar-bearing i
 * rule in sol.css; no JS animation is required.
 */
export function Scope({
  variant,
}: {
  variant: "brand" | "mini";
}): JSX.Element {
  return (
    <span className={variant === "brand" ? "brand-scope" : "mini-scope"} aria-hidden="true">
      <i />
    </span>
  );
}