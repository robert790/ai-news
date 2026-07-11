import type { ReactNode } from "react";

/**
 * Panel — raised or recessed module container.
 * Use raised for hero cards / instrument housings,
 * recessed for inset data displays.
 *
 * Slots: header (top-right controls), title (left of header),
 * children (body).
 */
export interface PanelProps {
  title?: ReactNode;
  headerRight?: ReactNode;
  variant?: "raised" | "recessed";
  /** Show the four corner socket-head fasteners (decorative). */
  fasteners?: boolean;
  /** aria-label for the panel region. Falls back to title if string. */
  ariaLabel?: string;
  className?: string;
  children: ReactNode;
}

export function Panel({
  title,
  headerRight,
  variant = "raised",
  fasteners = false,
  ariaLabel,
  className,
  children,
}: PanelProps) {
  const base = variant === "recessed" ? "ort-panel-recessed" : "ort-panel";
  const label =
    ariaLabel ?? (typeof title === "string" ? title : undefined);
  return (
    <section
      aria-label={label}
      className={[
        base,
        "relative",
        className ?? "",
      ]
        .filter(Boolean)
        .join(" ")}
    >
      {fasteners && (
        <>
          <span className="absolute top-2 left-2 ort-fastener" aria-hidden="true" />
          <span className="absolute top-2 right-2 ort-fastener" aria-hidden="true" />
          <span className="absolute bottom-2 left-2 ort-fastener" aria-hidden="true" />
          <span className="absolute bottom-2 right-2 ort-fastener" aria-hidden="true" />
        </>
      )}
      {(title || headerRight) && (
        <header className="ort-panel-header">
          <div className="ort-panel-title">{title}</div>
          {headerRight && (
            <div className="flex items-center gap-2 text-data text-xs">
              {headerRight}
            </div>
          )}
        </header>
      )}
      <div>{children}</div>
    </section>
  );
}