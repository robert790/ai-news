import type { ReactNode } from "react";

/**
 * ContentModule — a typed body of static editorial content.
 * Wraps prose inside a Panel so it shares the chassis construction.
 */
export interface ContentModuleProps {
  title?: ReactNode;
  children: ReactNode;
  footer?: ReactNode;
}

export function ContentModule({ title, children, footer }: ContentModuleProps) {
  return (
    <div className="ort-content-module">
      {title && (
        <div
          className="text-label"
          style={{ marginBottom: "8px", fontSize: "10px" }}
        >
          {title}
        </div>
      )}
      <div>{children}</div>
      {footer && (
        <div
          className="hairline"
          style={{ marginTop: "12px", paddingTop: "10px", color: "var(--text-muted)", fontSize: "11px" }}
        >
          {footer}
        </div>
      )}
    </div>
  );
}