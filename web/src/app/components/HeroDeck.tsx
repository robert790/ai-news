import * as React from "react";
import { Bolt } from "./Machine";
import { Radar } from "./Radar";

/**
 * The hero panel. Renders the operational-console label, the
 * headline, the lede, the three action buttons, the overview
 * link, the optional side grips, the four corner bolts, and the
 * radar.
 *
 * DOM contract: the inner `.hero-copy` div contains the kicker,
 * h1, rule, lede, actions, and overview link in that order. The
 * `<Radar />` follows as a sibling.
 */
export function HeroDeck({
  kicker,
  title,
  lede,
  actions,
  overview,
  withGrips = true,
  heroTitleId = "hero-title",
}: {
  kicker: string;
  /** Headline content. Rendered verbatim; pass a string or JSX with `<br/>`. */
  title: React.ReactNode;
  lede: string;
  /** Three CTAs. First is primary (filled). */
  actions: ReadonlyArray<{ label: React.ReactNode; href: string; primary?: boolean }>;
  overview?: { label: string; href: string };
  /** Show the side grip rivets. Default true (desktop). */
  withGrips?: boolean;
  /** id for the h1 (used for aria-labelledby). */
  heroTitleId?: string;
}): JSX.Element {
  return (
    <section className="hero-deck" aria-labelledby={heroTitleId}>
      {withGrips ? (
        <>
          <span className="grip grip--left" aria-hidden="true" />
          <span className="grip grip--right" aria-hidden="true" />
        </>
      ) : null}
      <Bolt className="hero-bolt hero-bolt--tl" />
      <Bolt className="hero-bolt hero-bolt--tr" />
      <Bolt className="hero-bolt hero-bolt--bl" />
      <Bolt className="hero-bolt hero-bolt--br" />
      <div className="hero-copy">
        <p className="kicker">
          <i /> {kicker}
        </p>
        <h1 id={heroTitleId}>{title}</h1>
        <span className="rule" aria-hidden="true" />
        <p className="lede">{lede}</p>
        <div className="hero-actions">
          {actions.map((a, i) => (
            <a
              key={i}
              className={a.primary ? "primary-action" : undefined}
              href={a.href}
            >
              {a.label}
            </a>
          ))}
        </div>
        {overview ? (
          <a className="overview" href={overview.href}>
            <i>▶</i> {overview.label}
          </a>
        ) : null}
      </div>
      <Radar />
    </section>
  );
}