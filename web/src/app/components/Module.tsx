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
}: {
  title: string;
  code: string;
  children: React.ReactNode;
  className?: string;
}): JSX.Element {
  return (
    <article className={`module ${className}`}>
      <header className="module-head">
        <span className="module-code">{code}</span>
        <h2>{title}</h2>
        <button type="button">
          View all <b>›</b>
        </button>
      </header>
      <div className="module-body">{children}</div>
    </article>
  );
}