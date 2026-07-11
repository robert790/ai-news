import type { ReactNode } from "react";

export interface AlertStripProps {
  variant?: "info" | "warn" | "err";
  icon?: ReactNode;
  children: ReactNode;
}

export function AlertStrip({ variant = "info", icon, children }: AlertStripProps) {
  const cls =
    variant === "warn" ? "ort-alert ort-alert--warn" : variant === "err" ? "ort-alert ort-alert--err" : "ort-alert";
  return (
    <div className={cls} role={variant === "err" ? "alert" : "status"}>
      {icon && (
        <span aria-hidden="true" style={{ color: "var(--signal-primary)" }}>
          {icon}
        </span>
      )}
      <span>{children}</span>
    </div>
  );
}