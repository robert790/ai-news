"use client";

import type { ReactNode } from "react";

export interface SegmentedOption<T extends string> {
  value: T;
  label: ReactNode;
  ariaLabel?: string;
}

export interface SegmentedProps<T extends string> {
  options: ReadonlyArray<SegmentedOption<T>>;
  value: T;
  onChange: (next: T) => void;
  ariaLabel: string;
}

/**
 * Segmented — pill-style mutually-exclusive selector.
 * Uses `aria-pressed` so each item is a real toggle button.
 * Keyboard: Tab into group, Arrow keys to move, Space/Enter to activate.
 */
export function Segmented<T extends string>({
  options,
  value,
  onChange,
  ariaLabel,
}: SegmentedProps<T>) {
  const onKey = (e: React.KeyboardEvent<HTMLDivElement>) => {
    if (e.key !== "ArrowRight" && e.key !== "ArrowLeft") return;
    e.preventDefault();
    const idx = options.findIndex((o) => o.value === value);
    if (idx === -1) return;
    const next =
      e.key === "ArrowRight"
        ? (idx + 1) % options.length
        : (idx - 1 + options.length) % options.length;
    onChange(options[next].value);
  };
  return (
    <div
      role="group"
      aria-label={ariaLabel}
      className="ort-segmented"
      onKeyDown={onKey}
    >
      {options.map((o) => {
        const selected = o.value === value;
        return (
          <button
            key={o.value}
            type="button"
            aria-pressed={selected}
            aria-label={o.ariaLabel ?? (typeof o.label === "string" ? o.label : o.value)}
            onClick={() => onChange(o.value)}
            className="ort-segmented__item"
          >
            {o.label}
          </button>
        );
      })}
    </div>
  );
}