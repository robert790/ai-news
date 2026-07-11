import * as React from "react";
import { Brand } from "./Brand";

export type NavLink = { label: string; href: string; active?: boolean };

/**
 * Top navigation deck. Contains the brand mark, the 5-up nav strip,
 * the utility action cluster (3 buttons + dial), the mobile menu
 * trigger, and the online indicator.
 *
 * The freeze DOM is rendered verbatim — class names, ordering,
 * and aria-labels are preserved.
 */
export function TopDeck({
  nav,
}: {
  nav: readonly NavLink[];
}): JSX.Element {
  return (
    <header className="top-deck">
      <Brand />
      <nav aria-label="Main navigation">
        {nav.map((item) => (
          <a key={item.label} className={item.active ? "active" : undefined} href={item.href}>
            {item.label}
          </a>
        ))}
      </nav>
      <div className="top-actions" aria-label="Utilities">
        <button aria-label="Search">⌕</button>
        <button aria-label="Saved items">▯</button>
        <button aria-label="Notifications">♢</button>
        <span className="dial" aria-hidden="true" />
      </div>
      <button className="menu" type="button" aria-label="Open navigation">
        <span /> Menu
      </button>
      <div className="online">
        <i /> System online
      </div>
    </header>
  );
}

export const HOME_NAV: readonly NavLink[] = [
  { label: "Home", href: "#", active: true },
  { label: "Tools", href: "#tools" },
  { label: "Prompt Kits", href: "#kits" },
  { label: "Learn", href: "#learn" },
  { label: "Jobs", href: "#jobs" },
];