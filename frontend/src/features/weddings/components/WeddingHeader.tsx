import { memo } from "react";
import type { WeddingOut } from "@/api/generated/v1/models/weddingOut";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Skeleton } from "@/components/ui/skeleton";
import { Calendar, MapPin, Pencil, Users } from "lucide-react";
import { getWeddingStatusBadgeStyle, getWeddingStatusLabel } from "@/features/weddings/utils/wedding-status";
import { cn } from "@/lib/utils";
import { TEMPLATE_MAP } from "../constants";

interface WeddingHeaderProps {
  wedding: WeddingOut;
  displayDate: string;
  checklistPercentage: number;
  isLoadingOverview?: boolean;
  onEditClick: () => void;
}

export const WeddingHeader = memo(function WeddingHeader({
  wedding,
  displayDate,
  checklistPercentage,
  isLoadingOverview = false,
  onEditClick,
}: WeddingHeaderProps) {
  const templateLabel = wedding.template ? (TEMPLATE_MAP[wedding.template] ?? wedding.template) : null;
  const statusStyle = getWeddingStatusBadgeStyle(wedding.status);
  const statusLabel = getWeddingStatusLabel(wedding.status);

  const formatBudget = (amount?: number | null) => {
    if (amount === undefined || amount === null) return "R$ —";
    if (amount >= 1000) {
      const value = amount / 1000;
      return `R$ ${value % 1 === 0 ? value : value.toFixed(1)}k`;
    }
    return `R$ ${amount}`;
  };

  return (
    <div className="bg-white dark:bg-[#18181B] p-4 rounded-xl border border-zinc-200 dark:border-zinc-800 shadow-sm relative overflow-hidden">
      {/* Decorative corner background */}
      <div className="absolute right-0 top-0 w-16 h-16 bg-primary/5 rounded-bl-full pointer-events-none" />

      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 relative z-10">
        {/* Left Block: Names, Category, Date, Location & Guests */}
        <div className="flex flex-col gap-1.5">
          {/* Row 1: Names and Style badge + Status badge + Edit button */}
          <div className="flex flex-wrap items-center gap-2.5">
            <h2 className="font-display text-xl sm:text-2xl font-bold text-zinc-900 dark:text-white tracking-tight">
              {wedding.groom_name} & {wedding.bride_name}
            </h2>
            {templateLabel && (
              <span className="bg-zinc-100 dark:bg-zinc-800 text-zinc-600 dark:text-zinc-400 text-[10px] px-2 py-0.5 rounded font-bold uppercase tracking-wider">
                {templateLabel}
              </span>
            )}
            {statusStyle && (
              <span
                className={cn(
                  "inline-flex items-center px-2.5 py-0.5 rounded border text-[10px] font-bold uppercase tracking-wider shadow-sm",
                  statusStyle.className
                )}
              >
                {statusStyle.dotClassName && (
                  <span
                    className={cn(
                      "w-1.5 h-1.5 rounded-full mr-1.5 animate-pulse",
                      statusStyle.dotClassName
                    )}
                  />
                )}
                {statusStyle.icon === "check" && (
                  <span className="mr-1">✓</span>
                )}
                {statusLabel}
              </span>
            )}
            <Button
              variant="ghost"
              size="icon"
              className="h-7 w-7 text-zinc-400 hover:text-zinc-600 hover:bg-zinc-100 dark:hover:bg-zinc-800 dark:hover:text-zinc-200 rounded-full cursor-pointer transition-colors"
              onClick={onEditClick}
              title="Editar dados do casamento"
            >
              <Pencil className="h-3.5 w-3.5" />
            </Button>
          </div>

          {/* Row 2: Date, Address, and Guests consolidated */}
          <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-zinc-500 dark:text-zinc-400 font-medium">
            <span className="flex items-center gap-1.5">
              <Calendar className="h-3.5 w-3.5 opacity-80" /> {displayDate}
            </span>
            <span className="text-zinc-300 dark:text-zinc-800/40 hidden sm:inline">•</span>
            <span className="flex items-center gap-1.5">
              <MapPin className="h-3.5 w-3.5 opacity-80" /> {wedding.location}
            </span>
            <span className="text-zinc-300 dark:text-zinc-800/40 hidden sm:inline">•</span>
            <span className="flex items-center gap-1.5">
              <Users className="h-3.5 w-3.5 opacity-80" /> {wedding.expected_guests ? `${wedding.expected_guests} Convidados` : "— Convidados"}
            </span>
          </div>
        </div>

        {/* Right Block: Compact financial bar + Checklist slider in line */}
        <div className="flex items-center gap-4 divide-x divide-zinc-200 dark:divide-zinc-800 shrink-0">
          <div className="text-left pl-0">
            <span className="block text-[9px] font-bold text-zinc-400 dark:text-zinc-500 uppercase tracking-wider">Orçado</span>
            <span className="block font-mono text-base font-bold text-zinc-950 dark:text-white">
              {formatBudget(wedding.total_budget)}
            </span>
          </div>
          <div className="text-left pl-4 space-y-1">
            <div className="flex items-center justify-between gap-3">
              <span className="text-[9px] font-bold text-zinc-400 dark:text-zinc-500 uppercase tracking-wider">Checklist</span>
              {isLoadingOverview ? (
                <Skeleton className="h-3 w-8" />
              ) : (
                <span className="font-mono text-[10px] font-bold text-zinc-700 dark:text-zinc-300">
                  {checklistPercentage}%
                </span>
              )}
            </div>
            {isLoadingOverview ? (
              <Skeleton className="h-1.5 w-24 rounded-full" />
            ) : (
              <Progress value={checklistPercentage} className="h-1.5 w-24" />
            )}
          </div>
        </div>
      </div>
    </div>
  );
});
