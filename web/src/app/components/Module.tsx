import * as React from "react";

/**
 * Header + body module card (Featured tools / Prompt kits /
 * Learn path / Jobs).
 *
 * DOM contract:
 *   <article class="module {className}">
 *     <header class="module-head">
 *       <span class="module-code">{code}</span>
 *       <h2>{title}</h2>
 *       <button type="button">View all <b>›</b></button>
 *     </header>
 *     <div class="module-body">{children}</div>
 *   </article>
 */
export function Module({
  title,
  code,
  children,
  className = "",
  id,
  actionHref,
  actionLabel = "View all",
  specimen = false,
}: {
  title: string;
  code: string;
  children: React.ReactNode;
  className?: string;
  id?: string;
  actionHref?: string;
  actionLabel?: string;
  /** Explicit specimen badge. Only /system opts in. */
  specimen?: boolean;
}): JSX.Element {
  return (
    <article className={`module ${className}`} id={id}>
      <header className="module-head">
        <span className="module-code">{code}</span>
        <h2>{title}</h2>
        {actionHref ? (
          <a href={actionHref}>
            {actionLabel} <b>›</b>
          </a>
        ) : specimen ? (
          <span
            className="module-head__specimen"
            aria-hidden="true"
          >
            Specimen
          </span>
        ) : null}
      </header>
      <div className="module-body">{children}</div>
    </article>
  );
}