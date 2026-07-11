import type { ReactNode } from "react";

export interface ListItemProps {
  title: ReactNode;
  meta?: ReactNode;
  selected?: boolean;
  onSelect?: () => void;
  trailing?: ReactNode;
  ariaLabel?: string;
}

/**
 * ListItem — generic module-row list item.
 * Real interactive surface when onSelect is provided.
 * aria-selected when part of a selectable list.
 */
export function ListItem({
  title,
  meta,
  selected,
  onSelect,
  trailing,
  ariaLabel,
}: ListItemProps) {
  const interactive = typeof onSelect === "function";
  const content = (
    <>
      <div className="flex flex-col">
        <span style={{ color: "var(--text-primary)", fontSize: "13px" }}>
          {title}
        </span>
        {meta && (
          <span
            className="text-data"
            style={{ fontSize: "10px", color: "var(--text-muted)" }}
          >
            {meta}
          </span>
        )}
      </div>
      {trailing && <span className="ml-auto">{trailing}</span>}
    </>
  );
  if (interactive) {
    return (
      <button
        type="button"
        aria-label={ariaLabel}
        aria-pressed={selected}
        onClick={onSelect}
        className="ort-list-item w-full text-left"
        style={{ background: "none", border: "none" }}
      >
        {content}
      </button>
    );
  }
  return (
    <div aria-selected={selected} className="ort-list-item">
      {content}
    </div>
  );
}