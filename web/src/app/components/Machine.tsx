import * as React from "react";

/**
 * Machine chassis frame.
 *
 * Renders the bronze-trimmed, bolt-cornered console chassis. The
 * bolt children are the decorative rivets that anchor the visual
 * identity. The freeform `children` are the inner panels (top
 * deck, hero deck, status rail, modules, lower bank, footer).
 *
 * When `skin` is set, the chassis renders `data-skin="…"` so the
 * accent preset selectors in globals.css take effect. The
 * attribute is omitted entirely otherwise (to keep the rendered
 * DOM identical to the freeze when no skin is supplied).
 *
 * DOM contract (with no skin, no ariaLabel):
 *   <div class="machine">
 *     <span class="bolt machine-bolt machine-bolt--tl" aria-hidden="true"/>
 *     <span class="bolt machine-bolt machine-bolt--tr" aria-hidden="true"/>
 *     <span class="bolt machine-bolt machine-bolt--bl" aria-hidden="true"/>
 *     <span class="bolt machine-bolt machine-bolt--br" aria-hidden="true"/>
 *     {children}
 *   </div>
 */
export function Machine({
  children,
  skin,
  ariaLabel,
}: {
  children: React.ReactNode;
  /** Optional accent preset. Defaults to the freeze (green). */
  skin?: "green" | "amber" | "cyan" | "red" | "violet";
  /** Optional aria-label for the chassis landmark. */
  ariaLabel?: string;
}): JSX.Element {
  return (
    <div
      className="machine"
      {...(skin ? { "data-skin": skin } : {})}
      {...(ariaLabel ? { "aria-label": ariaLabel } : {})}
    >
      <Bolt className="machine-bolt machine-bolt--tl" />
      <Bolt className="machine-bolt machine-bolt--tr" />
      <Bolt className="machine-bolt machine-bolt--bl" />
      <Bolt className="machine-bolt machine-bolt--br" />
      {children}
    </div>
  );
}

/**
 * Decorative bolt rivet. Used inside the machine and inside the
 * hero deck. Always aria-hidden.
 */
export function Bolt({ className = "" }: { className?: string }): JSX.Element {
  return <span className={`bolt ${className}`} aria-hidden="true" />;
}