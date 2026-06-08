import { lazy, Suspense, useState } from "react";
import { Link } from "react-router-dom";
import { useWeddingsList } from "@/api/generated/v1/endpoints/weddings/weddings";
import { useDashboardSummary, useDashboardWedding } from "@/api/generated/v1/endpoints/dashboard/dashboard";
import { StatsCards } from "@/features/dashboard/components/StatsCards";
import { WeddingStatsCards } from "@/features/dashboard/components/WeddingStatsCards";
import { WeddingBudgetBreakdown } from "@/features/dashboard/components/WeddingBudgetBreakdown";
import { CriticalWeddings } from "@/features/dashboard/components/CriticalWeddings";
import { DashboardOperations } from "@/features/dashboard/components/DashboardOperations";
import { UpcomingAppointments } from "@/features/dashboard/components/UpcomingAppointments";
import { UpcomingInstallments } from "@/features/dashboard/components/UpcomingInstallments";
import { getApiErrorInfo } from "@/api/error-utils";
import { useAuthStore } from "@/stores/authStore";
import { getWeddingStatusInfo } from "@/features/weddings/utils/wedding-status";

import { Skeleton } from "@/components/ui/skeleton";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  AlertCircle,
  Calendar,
  Heart,
  MapPin,
  ArrowRight,
  ExternalLink,
} from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
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

export default function DashboardPage() {
  const now = new Date();
  const [selectedYear, setSelectedYear] = useState(now.getFullYear());
  const [selectedWeddingUuid, setSelectedWeddingUuid] = useState<string>("all");
  const firstName = useAuthStore((state) => state.user?.first_name);

  const { data, isLoading, error } = useWeddingsList();
  const { data: summaryData } = useDashboardSummary();

  const isWeddingSelected = selectedWeddingUuid !== "all";

  const { data: weddingDashboardData, isLoading: isLoadingWeddingDashboard } =
    useDashboardWedding(selectedWeddingUuid, {
      query: { enabled: isWeddingSelected },
    });

  if (isLoading) {
    return (
      <div className="flex-1 overflow-auto min-h-screen">
        <div className="max-w-7xl mx-auto space-y-8 py-6 px-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div className="space-y-2">
              <Skeleton className="h-10 w-64" />
              <Skeleton className="h-4 w-48" />
            </div>
            <Skeleton className="h-10 w-32 rounded-lg" />
          </div>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            {[...Array(4)].map((_, i) => (
              <Skeleton key={i} className="h-32 w-full rounded-xl shadow-sm" />
            ))}
          </div>
          <div className="grid gap-6 lg:grid-cols-3">
            <Skeleton className="h-100 lg:col-span-2 rounded-xl shadow-sm" />
            <Skeleton className="h-100 rounded-xl shadow-sm" />
          </div>
          <Skeleton className="h-87.5 w-full rounded-xl shadow-sm" />
        </div>
      </div>
    );
  }

  if (error) {
    const { message } = getApiErrorInfo(
      error,
      "Não foi possível carregar os dados do painel.",
    );
    return (
      <div className="max-w-7xl mx-auto py-8 px-4">
        <Alert variant="destructive">
          <AlertCircle className="size-4" />
          <AlertTitle>Erro</AlertTitle>
          <AlertDescription>{message}</AlertDescription>
        </Alert>
      </div>
    );
  }

  const weddingsArray = data?.data.items ?? [];
  const summary = summaryData?.data;
  const weddingDashboard = weddingDashboardData?.data;

  const selectedWedding = weddingsArray.find(
    (w) => w.uuid === selectedWeddingUuid,
  );

  const greetingHour = now.getHours();
  const greeting =
    greetingHour < 12
      ? "Bom dia"
      : greetingHour < 18
        ? "Boa tarde"
        : "Boa noite";

  const formattedDate = now.toLocaleDateString("pt-BR", {
    day: "numeric",
    month: "long",
    year: "numeric",
  });

  const weddingStatusInfo = selectedWedding
    ? getWeddingStatusInfo(selectedWedding.status)
    : null;

  const weddingDate = selectedWedding
    ? new Date(selectedWedding.date).toLocaleDateString("pt-BR", {
        day: "2-digit",
        month: "long",
        year: "numeric",
        timeZone: "UTC",
      })
    : null;

  return (
    <div className="flex-1 overflow-auto min-h-screen">
      <div className="max-w-7xl mx-auto space-y-8 animate-in fade-in duration-500">
        {/* Welcome + Filters */}
        <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4">
          <div>
            <h1 className="font-display text-2xl sm:text-3xl font-bold text-zinc-900 dark:text-white tracking-tight">
              {greeting}, {firstName || "Helena"}
            </h1>
            <p className="text-zinc-500 dark:text-zinc-400 mt-1">
              {isWeddingSelected && selectedWedding
                ? `Visualizando: ${selectedWedding.bride_name} & ${selectedWedding.groom_name}`
                : "Aqui está o panorama financeiro e de eventos para hoje."}
            </p>
          </div>

          <div className="flex items-center gap-3">
            {/* Wedding filter */}
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

            {/* Date badge */}
            <div className="hidden sm:flex items-center gap-2 text-sm text-zinc-500 dark:text-zinc-400 bg-white dark:bg-[#18181B] px-4 py-2 rounded-lg border border-zinc-200 dark:border-zinc-800 shadow-sm font-medium shrink-0">
              <Calendar className="w-4 h-4 text-primary" />
              {formattedDate}
            </div>
          </div>
        </div>

        {/* Wedding Header — only in individual view */}
        {isWeddingSelected && selectedWedding && (
          <div className="bg-gradient-to-r from-aura-50 to-white dark:from-zinc-900 dark:to-zinc-950 border border-aura-100 dark:border-zinc-800 rounded-xl p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4 shadow-soft animate-in fade-in slide-in-from-top-2 duration-300">
            <div className="flex items-start gap-4">
              <div className="w-12 h-12 rounded-xl bg-aura-100 dark:bg-aura-900/40 flex items-center justify-center text-aura-600 dark:text-aura-400 border border-aura-200 dark:border-aura-800/50 shrink-0">
                <Heart className="w-6 h-6 fill-current opacity-80" />
              </div>
              <div>
                <div className="flex items-center gap-2 flex-wrap">
                  <h2 className="text-lg font-bold text-zinc-900 dark:text-white">
                    {selectedWedding.bride_name} & {selectedWedding.groom_name}
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
                    {selectedWedding.location}
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
                <Link to={`/weddings/${selectedWedding.uuid}`}>
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
                <Link to={`/weddings/${selectedWedding.uuid}?tab=finances`}>
                  Finanças <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </Button>
            </div>
          </div>
        )}

        {/* KPI Grid — Global or Individual */}
        {isWeddingSelected ? (
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
                  weddings={weddingsArray}
                  selectedYear={selectedYear}
                  onYearChange={setSelectedYear}
                />
              </Suspense>
              <UpcomingAppointments />
            </>
          )}
        </div>

        <UpcomingInstallments />

        {/* Recent Weddings — only in global view */}
        {!isWeddingSelected && (
          <div className="grid gap-6">
            <DashboardOperations weddings={weddingsArray} />
          </div>
        )}
      </div>
    </div>
  );
}
