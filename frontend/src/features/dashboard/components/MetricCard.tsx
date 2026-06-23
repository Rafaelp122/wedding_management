import { type ReactNode } from "react";
import { cn } from "@/lib/utils";
import type { Severity } from "../utils";
import { severityStyles } from "../utils";

interface MetricCardProps {
  label: string;
  value: ReactNode;
  icon: ReactNode;
  severity?: Severity;
  statusLabel?: string;
  sheetTrigger?: ReactNode;
  children?: ReactNode;
}

export function MetricCard({
  label,
  value,
  icon,
  severity = "neutral",
  statusLabel,
  sheetTrigger,
  children,
}: MetricCardProps) {
  const styles = severityStyles[severity];

  return (
    <div
      className={cn(
        "bg-card p-5 rounded-xl shadow-soft relative overflow-hidden group border",
        styles.border,
      )}
    >
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div
            className={cn(
              "w-10 h-10 rounded-lg flex items-center justify-center border",
              styles.iconBg,
            )}
          >
            <span className={cn("size-5", styles.iconColor)}>{icon}</span>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">{label}</p>
            <p className={cn("text-2xl font-bold tracking-tight", styles.text)}>
              {value}
            </p>
          </div>
        </div>
        {statusLabel && (
          <span
            className={cn(
              "text-xs font-medium px-2 py-1 rounded-full",
              styles.bg,
              styles.text,
            )}
          >
            {statusLabel}
          </span>
        )}
      </div>

      {children && <div className="mt-2">{children}</div>}

      {sheetTrigger && (
        <div className="mt-3 pt-3 border-t border-border">{sheetTrigger}</div>
      )}
    </div>
  );
}
