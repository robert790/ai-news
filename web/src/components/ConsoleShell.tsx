import type { ReactNode } from "react";

/**
 * ConsoleShell — the outermost machine frame.
 * Wraps every page. Provides the chassis background, padding,
 * bronze perimeter hairline, and responsive width.
 *
 * Pure presentational component. No data, no state.
 */
export interface ConsoleShellProps {
  children: ReactNode;
  /** Optional max-width. Default is wide enough for 1440 desktop. */
  maxWidth?: number;
  /** Show bronze perimeter hairline (default true on /system, optional elsewhere). */
  bronzePerimeter?: boolean;
  /** Aria label for the chassis landmark. */
  ariaLabel?: string;
}

export function ConsoleShell({
  children,
  maxWidth = 1320,
  bronzePerimeter = true,
  ariaLabel = "Console",
}: ConsoleShellProps) {
  const cls = ["ort-chassis", bronzePerimeter ? "ort-chassis-bronze" : ""]
    .filter(Boolean)
    .join(" ");
  return (
    <div
      role="region"
      aria-label={ariaLabel}
      className={cls}
      style={{
        margin: "0 auto",
        padding: "20px",
        maxWidth: `${maxWidth}px`,
        width: "100%",
      }}
    >
      {children}
    </div>
  );
}