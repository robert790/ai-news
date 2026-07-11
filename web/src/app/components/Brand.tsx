import * as React from "react";
import { Scope } from "./Scope";

/**
 * Brand mark (scope + wordmark + tagline). The `href` defaults to
 * the home anchor and the aria-label is fixed.
 */
export function Brand({
  href = "#",
  wordmark = "OPEN · RADAR",
  tagline = "AI tools · prompts · learn · jobs",
}: {
  href?: string;
  wordmark?: string;
  tagline?: string;
}): JSX.Element {
  return (
    <a className="brand" href={href} aria-label="OpenRadar home">
      <Scope variant="brand" />
      <span>
        <strong>{wordmark}</strong>
        <small>{tagline}</small>
      </span>
    </a>
  );
}