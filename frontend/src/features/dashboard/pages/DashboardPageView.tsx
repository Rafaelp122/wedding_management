import { lazy, Suspense } from "react";
import { Link } from "react-router-dom";
import type { WeddingOut } from "@/api/generated/v1/models/weddingOut";
import type { WeddingLookupOut } from "@/api/generated/v1/models/weddingLookupOut";
import type { DashboardSummaryOut } from "@/api/generated/v1/models/dashboardSummaryOut";
import type { WeddingDashboardOut } from "@/api/generated/v1/models/weddingDashboardOut";
import { StatsCards } from "@/features/dashboard/components/StatsCards";
import { WeddingStatsCards } from "@/features/dashboard/components/WeddingStatsCards";
import { WeddingBudgetBreakdown } from "@/features/dashboard/components/WeddingBudgetBreakdown";
import { CriticalWeddings } from "@/features/dashboard/components/CriticalWeddings";
import { DashboardOperations } from "@/features/dashboard/components/DashboardOperations";
import { UpcomingAppointments } from "@/features/dashboard/components/UpcomingAppointments";
import { UpcomingInstallments } from "@/features/dashboard/components/UpcomingInstallments";

import { Skeleton } from "@/components/ui/skeleton";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Calendar,
  Heart,
  MapPin,
  ArrowRight,
  ExternalLink,
} from "lucide-react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

const WeddingMonthlyChart = lazy(() =>
  import("@/features/dashboard/components/WeddingMonthlyChart").then((m) => ({
    default: m.WeddingMonthlyChart,
  })),
);

interface DashboardPageViewProps {
  greeting: string;
  formattedDate: string;
  firstName: string | undefined;
  selectedYear: number;
  setSelectedYear: (year: number) => void;
  selectedWeddingUuid: string;
  setSelectedWeddingUuid: (uuid: string) => void;
  isLoadingLookup: boolean;
  weddingsArray: WeddingLookupOut[];
  isWeddingSelected: boolean;
  selectedWeddingFull: WeddingOut | null;
  selectedWedding: WeddingLookupOut | null;
  weddingStatusInfo: { label: string; variant: "default" | "secondary" | "destructive" | "outline" } | null;
  weddingDate: string | null;
  isLoadingWeddingDashboard: boolean;
  weddingDashboard: WeddingDashboardOut | undefined;
  summary: DashboardSummaryOut | undefined;
  fullWeddingsArray: WeddingOut[];
}

export function DashboardPageView({
  greeting,
  formattedDate,
  firstName,
  selectedYear,
  setSelectedYear,
  selectedWeddingUuid,
  setSelectedWeddingUuid,
  isLoadingLookup,
  weddingsArray,
  isWeddingSelected,
  selectedWeddingFull,
  selectedWedding,
  weddingStatusInfo,
  weddingDate,
  isLoadingWeddingDashboard,
  weddingDashboard,
  summary,
  fullWeddingsArray,
}: DashboardPageViewProps) {
  return (
    <div className="flex-1 overflow-auto min-h-screen">
      <div className="max-w-7xl mx-auto space-y-8 animate-in fade-in duration-500">
        {/* Welcome + Filters */}
        <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4">
          <div>
            <h1 className="font-display text-2xl sm:text-3xl font-bold text-zinc-900 dark:text-white tracking-tight">
              {greeting}{firstName && `, ${firstName}`}
            </h1>
            <p className="text-zinc-500 dark:text-zinc-400 mt-1">
              {isWeddingSelected && selectedWedding
                ? `Visualizando: ${selectedWedding.bride_name} & ${selectedWedding.groom_name}`
                : "Aqui está o panorama financeiro e de eventos para hoje."}
            </p>
          </div>

          <div className="flex items-center gap-3">
            {/* Wedding filter */}
            {isLoadingLookup ? (
              <Skeleton className="h-10 w-52 rounded-lg" />
            ) : (
              <Select
                value={selectedWeddingUuid}
                onValueChange={setSelectedWeddingUuid}
              >
                <SelectTrigger
                  id="wedding-filter"
                  className="w-52 bg-white dark:bg-[#18181B] border-zinc-200 dark:border-zinc-800 shadow-sm text-sm font-medium text-zinc-700 dark:text-zinc-300"
                >
                  <div className="flex items-center gap-2 truncate">
                    <Heart className="w-3.5 h-3.5 text-aura-500 shrink-0" />
                    <SelectValue placeholder="Todos os Casamentos" />
                  </div>
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Todos os Casamentos</SelectItem>
                  {weddingsArray.map((wedding) => (
                    <SelectItem key={wedding.uuid} value={wedding.uuid}>
                      {wedding.bride_name} &amp; {wedding.groom_name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            )}

            {/* Date badge */}
            <div className="hidden sm:flex items-center gap-2 text-sm text-zinc-500 dark:text-zinc-400 bg-white dark:bg-[#18181B] px-4 py-2 rounded-lg border border-zinc-200 dark:border-zinc-800 shadow-sm font-medium shrink-0">
              <Calendar className="w-4 h-4 text-primary" />
              {formattedDate}
            </div>
          </div>
        </div>

        {/* Wedding Header — only in individual view */}
        {isWeddingSelected && selectedWeddingFull && (
          <div className="bg-gradient-to-r from-aura-50 to-white dark:from-zinc-900 dark:to-zinc-950 border border-aura-100 dark:border-zinc-800 rounded-xl p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4 shadow-soft animate-in fade-in slide-in-from-top-2 duration-300">
            <div className="flex items-start gap-4">
              <div className="w-12 h-12 rounded-xl bg-aura-100 dark:bg-aura-900/40 flex items-center justify-center text-aura-600 dark:text-aura-400 border border-aura-200 dark:border-aura-800/50 shrink-0">
                <Heart className="w-6 h-6 fill-current opacity-80" />
              </div>
              <div>
                <div className="flex items-center gap-2 flex-wrap">
                  <h2 className="text-lg font-bold text-zinc-900 dark:text-white">
                    {selectedWeddingFull.bride_name} & {selectedWeddingFull.groom_name}
                  </h2>
                  {weddingStatusInfo && (
                    <Badge
                      variant={weddingStatusInfo.variant}
                      className="text-xs"
                    >
                      {weddingStatusInfo.label}
                    </Badge>
                  )}
                </div>
                <div className="flex items-center gap-4 mt-1 text-sm text-zinc-500 dark:text-zinc-400 flex-wrap">
                  <span className="flex items-center gap-1">
                    <Calendar className="w-3.5 h-3.5" />
                    {weddingDate}
                  </span>
                  <span className="flex items-center gap-1">
                    <MapPin className="w-3.5 h-3.5" />
                    {selectedWeddingFull.location}
                  </span>
                </div>
              </div>
            </div>
            <div className="flex items-center gap-2 shrink-0">
              <Button
                asChild
                variant="outline"
                size="sm"
                className="border-aura-200 dark:border-aura-800/50 text-aura-700 dark:text-aura-400 hover:bg-aura-50 dark:hover:bg-aura-900/30 gap-1.5"
              >
                <Link to={`/weddings/${selectedWeddingFull.uuid}`}>
                  <ExternalLink className="w-3.5 h-3.5" />
                  Abrir casamento
                </Link>
              </Button>
              <Button
                asChild
                variant="ghost"
                size="sm"
                className="text-zinc-500 gap-1"
              >
                <Link to={`/weddings/${selectedWeddingFull.uuid}?tab=finances`}>
                  Finanças <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </Button>
            </div>
          </div>
        )}

        {/* KPI Grid — Global or Individual */}
        {isLoadingLookup ? (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            {[...Array(4)].map((_, i) => (
              <Skeleton key={i} className="h-32 w-full rounded-xl shadow-sm" />
            ))}
          </div>
        ) : isWeddingSelected ? (
          <WeddingStatsCards
            data={weddingDashboard}
            isLoading={isLoadingWeddingDashboard}
          />
        ) : (
          <StatsCards summary={summary} />
        )}

        {/* Critical Weddings — only in global view */}
        {!isWeddingSelected && (
          <CriticalWeddings weddings={summary?.critical_weddings ?? []} />
        )}

        {/* Main Content Grid */}
        {isLoadingLookup ? (
          <div className="grid gap-6 lg:grid-cols-3">
            <Skeleton className="h-80 lg:col-span-2 rounded-xl shadow-sm" />
            <Skeleton className="h-80 rounded-xl shadow-sm" />
          </div>
        ) : (
          <div className="grid gap-6 lg:grid-cols-3">
            {isWeddingSelected ? (
              /* Individual view: Budget Breakdown (2/3) + Agenda (1/3) */
              <>
                <div className="lg:col-span-2">
                  <WeddingBudgetBreakdown
                    categories={weddingDashboard?.categories_summary ?? []}
                    isLoading={isLoadingWeddingDashboard}
                  />
                </div>
                <UpcomingAppointments weddingUuid={selectedWeddingUuid} />
              </>
            ) : (
              /* Global view: Chart (2/3) + Agenda (1/3) */
              <>
                <Suspense
                  fallback={
                    <Skeleton className="h-80 lg:col-span-2 rounded-xl shadow-sm" />
                  }
                >
                  <WeddingMonthlyChart
                    selectedYear={selectedYear}
                    onYearChange={setSelectedYear}
                  />
                </Suspense>
                <UpcomingAppointments />
              </>
            )}
          </div>
        )}

        <UpcomingInstallments />

        {/* Recent Weddings — only in global view */}
        {!isWeddingSelected && (
          <div className="grid gap-6">
            <DashboardOperations weddings={fullWeddingsArray} />
          </div>
        )}
      </div>
    </div>
  );
}
