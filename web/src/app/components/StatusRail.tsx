import * as React from "react";

/**
 * One status rail cell. The first column is the icon slot — pass
 * a glyph in `.status-icon` for circular icons, or `.pulse` for
 * the animated EKG bar.
 *
 * DOM contract:
 *   <div>
 *     <i class="status-icon">…</i>
 *     <span>{label}<small>{detail}</small></span>
 *   </div>
 */
export function StatusRailItem({
  icon,
  label,
  detail,
}: {
  /** Pre-built icon element (e.g. <i class="status-icon">ϟ</i>). */
  icon: React.ReactNode;
  label: string;
  detail: string;
}): JSX.Element {
  return (
    <div>
      {icon}
      <span>
        {label}
        <small>{detail}</small>
      </span>
    </div>
  );
}

export function StatusRail({
  items,
  ariaLabel = "Current index status",
}: {
  items: ReadonlyArray<{ icon: React.ReactNode; label: string; detail: string }>;
  ariaLabel?: string;
}): JSX.Element {
  return (
    <section className="status-rail" aria-label={ariaLabel}>
      {items.map((item, i) => (
        <StatusRailItem key={i} {...item} />
      ))}
    </section>
  );
}