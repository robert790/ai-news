"use client";

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
  const [menuOpen, setMenuOpen] = React.useState(false);

  return (
    <header className={`top-deck ${menuOpen ? "top-deck--menu-open" : ""}`}>
      <Brand />
      <nav id="main-navigation" aria-label="Main navigation">
        {nav.map((item) => (
          <a
            key={item.label}
            className={item.active ? "active" : undefined}
            href={item.href}
            aria-current={item.active ? "page" : undefined}
            onClick={() => setMenuOpen(false)}
          >
            {item.label}
          </a>
        ))}
      </nav>
      <div className="top-actions" aria-label="Utilities">
        <button type="button" disabled title="Search — preview" aria-label="Search — preview only">⌕</button>
        <button type="button" disabled title="Saved items — preview" aria-label="Saved items — preview only">▯</button>
        <button type="button" disabled title="Notifications — preview" aria-label="Notifications — preview only">♢</button>
        <span className="dial" aria-hidden="true" />
      </div>
      <button
        className="menu"
        type="button"
        aria-label={`${menuOpen ? "Close" : "Open"} navigation`}
        aria-expanded={menuOpen}
        aria-controls="main-navigation"
        onClick={() => setMenuOpen((open) => !open)}
      >
        <span /> Menu
      </button>
      <div className="online">
        <i /> System online
      </div>
    </header>
  );
}

export const HOME_NAV: readonly NavLink[] = [
  { label: "Home", href: "/", active: true },
  { label: "Tools", href: "/tools" },
  { label: "Prompt Kits", href: "/prompt-kits" },
  { label: "Learn", href: "/#learn" },
  { label: "Jobs", href: "/#jobs" },
];