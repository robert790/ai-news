import * as React from "react";
import { Scope } from "./Scope";

export type FooterMeta = { dt: string; dd: string };

/**
 * The footer deck. Contains the brand mark block, the 4-up
 * definition list, the subscribe form, and the absolute-positioned
 * legal bar.
 *
 * The legal bar must remain the last child of `.footer-deck` so
 * the `position: absolute; bottom: 5px` rule pins it to the
 * bottom of the chassis.
 */
export type LegalItem =
  | { kind: "text"; value: string }
  | { kind: "status"; value: string }
  | { kind: "link"; value: string; href?: string }
  | { kind: "small"; value: string };

export function Footer({
  markTitle,
  markSubtitle,
  meta,
  subscribe,
  legal,
}: {
  markTitle: React.ReactNode;
  markSubtitle?: string;
  meta: ReadonlyArray<FooterMeta>;
  subscribe: { label: string; sublabel: string; placeholder: string; buttonLabel: string };
  legal: ReadonlyArray<LegalItem>;
}): JSX.Element {
  return (
    <footer className="footer-deck">
      <div className="footer-mark">
        <Scope variant="mini" />
        <p>
          <strong>{markTitle}</strong>
          {markSubtitle ? <small>{markSubtitle}</small> : null}
        </p>
      </div>
      <dl>
        {meta.map((m) => (
          <div key={m.dt}>
            <dt>{m.dt}</dt>
            <dd>{m.dd}</dd>
          </div>
        ))}
      </dl>
      <form aria-label="Preview only" noValidate>
        <label htmlFor="email">
          {subscribe.label} <small>{subscribe.sublabel}</small>
        </label>
        <span>
          <input id="email" type="email" placeholder={subscribe.placeholder} disabled aria-disabled="true" />
          <button type="button" aria-label={subscribe.buttonLabel} disabled>→</button>
        </span>
      </form>
      <div className="legal">
        {legal.map((item, i) => {
          if (item.kind === "link") {
            return (
              <a key={i} href={item.href ?? "#"}>
                {item.value}
              </a>
            );
          }
          if (item.kind === "status") {
            return (
              <span key={i}>
                {item.value} <i />
              </span>
            );
          }
          if (item.kind === "small") {
            return <small key={i}>{item.value}</small>;
          }
          return <span key={i}>{item.value}</span>;
        })}
      </div>
    </footer>
  );
}