export interface ProgressIndicatorProps {
  /** Number of segments total. */
  total: number;
  /** Number of segments lit. */
  value: number;
  ariaLabel: string;
}

export function ProgressIndicator({
  total,
  value,
  ariaLabel,
}: ProgressIndicatorProps) {
  const clamped = Math.max(0, Math.min(total, value));
  return (
    <div
      className="ort-progress"
      role="progressbar"
      aria-label={ariaLabel}
      aria-valuenow={clamped}
      aria-valuemin={0}
      aria-valuemax={total}
    >
      {Array.from({ length: total }).map((_, i) => (
        <span
          key={i}
          className={
            i < clamped ? "ort-progress__seg ort-progress__seg--on" : "ort-progress__seg"
          }
        />
      ))}
    </div>
  );
}