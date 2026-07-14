import * as React from "react";

/**
 * The 3-column lower bank beneath the module grid. Each panel has
 * a head line with a span label and a bold value, then a body.
 *
 * DOM contract:
 *   <section class="lower-bank">
 *     <div class="{panelClass}"><p>…</p>{body}</div>
 *     …
 *   </section>
 */
export function LowerBank({
  panels,
}: {
  panels: ReadonlyArray<{
    className: string;
    label: string;
    headline: string;
    body: React.ReactNode;
  }>;
}): JSX.Element {
  return (
    <section className="lower-bank">
      {panels.map((panel) => (
        <div key={panel.className} className={panel.className}>
          <p>
            <span>{panel.label}</span>
            <b>{panel.headline}</b>
          </p>
          {panel.body}
        </div>
      ))}
    </section>
  );
}