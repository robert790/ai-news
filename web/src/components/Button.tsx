import type { ButtonHTMLAttributes, ReactNode } from "react";

export type ButtonVariant = "primary" | "default" | "ghost";
export type ButtonSize = "md" | "sm";

export interface ButtonProps
  extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  leadingIcon?: ReactNode;
  trailingIcon?: ReactNode;
}

/**
 * Button — the single interactive button primitive.
 * Three variants: primary (phosphor fill), default (raised metal),
 * ghost (outline).
 *
 * Variants consume only token variables. No raw colors.
 */
export function Button({
  variant = "default",
  size = "md",
  leadingIcon,
  trailingIcon,
  children,
  className,
  ...rest
}: ButtonProps) {
  const variantCls =
    variant === "primary"
      ? "ort-btn ort-btn--primary"
      : variant === "ghost"
        ? "ort-btn ort-btn--ghost"
        : "ort-btn";
  const sizeCls = size === "sm" ? "ort-btn--sm" : "";
  return (
    <button
      {...rest}
      className={[variantCls, sizeCls, className ?? ""]
        .filter(Boolean)
        .join(" ")}
    >
      {leadingIcon && <span aria-hidden="true">{leadingIcon}</span>}
      <span>{children}</span>
      {trailingIcon && <span aria-hidden="true">{trailingIcon}</span>}
    </button>
  );
}