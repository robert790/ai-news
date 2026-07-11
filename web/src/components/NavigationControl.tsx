import type { ReactNode } from "react";

export interface NavigationControlProps {
  items: ReadonlyArray<{ id: string; label: string; href?: string }>;
  /** The id of the current page. */
  currentId?: string;
  /** Right-side accessory (e.g. search button, ThemeDial). */
  accessory?: ReactNode;
  ariaLabel?: string;
}

/**
 * NavigationControl — top instrument-strip nav.
 * Uses real <a>/<button> elements. Active item is aria-current="page".
 * Honors the same construction language as panels.
 */
export function NavigationControl({
  items,
  currentId,
  accessory,
  ariaLabel = "Primary navigation",
}: NavigationControlProps) {
  return (
    <nav
      aria-label={ariaLabel}
      className="flex flex-wrap items-center justify-between gap-3 md:gap-4 px-2 py-2"
    >
      <ul className="flex flex-wrap items-center gap-x-5 gap-y-2 list-none m-0 p-0">
        {items.map((it) => {
          const isCurrent = it.id === currentId;
          const content = (
            <>
              <span>{it.label}</span>
            </>
          );
          if (it.href) {
            return (
              <li key={it.id}>
                <a
                  href={it.href}
                  aria-current={isCurrent ? "page" : undefined}
                  className="ort-nav-item"
                >
                  {content}
                </a>
              </li>
            );
          }
          return (
            <li key={it.id}>
              <button
                type="button"
                aria-current={isCurrent ? "page" : undefined}
                className="ort-nav-item"
              >
                {content}
              </button>
            </li>
          );
        })}
      </ul>
      {accessory && <div className="flex items-center gap-3">{accessory}</div>}
    </nav>
  );
}