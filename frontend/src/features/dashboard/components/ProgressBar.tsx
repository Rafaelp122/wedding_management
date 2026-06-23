import { cn } from "@/lib/utils";

interface ProgressBarProps {
  percentage: number;
  className?: string;
  barClassName?: string;
}

export function ProgressBar({ percentage, className, barClassName }: ProgressBarProps) {
  const pct = Math.min(percentage, 100);
  const color =
    pct >= 90
      ? "bg-destructive"
      : pct >= 70
        ? "bg-amber-500"
        : "bg-aura-500";

  return (
    <div
      className={cn(
        "w-full bg-zinc-100 dark:bg-zinc-800 rounded-full h-2",
        className,
      )}
    >
      <div
        className={cn(
          "h-2 rounded-full transition-all duration-500",
          color,
          barClassName,
        )}
        style={{ width: `${pct}%` }}
      />
    </div>
  );
}
