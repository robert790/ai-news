import * as React from "react";

/**
 * Hero action button. Renders an `<a>` styled by `.hero-actions a`
 * (and `.primary-action` when `primary`).
 */
export function ActionButton({
  href,
  primary = false,
  children,
}: {
  href: string;
  primary?: boolean;
  children: React.ReactNode;
}): JSX.Element {
  return (
    <a className={primary ? "primary-action" : undefined} href={href}>
      {children}
    </a>
  );
}