import { lazy, Suspense, useState } from "react";
import { useWeddingsList } from "@/api/generated/v1/endpoints/weddings/weddings";
import { useDashboardSummary } from "@/api/generated/v1/endpoints/dashboard/dashboard";
import { StatsCards } from "@/features/dashboard/components/StatsCards";
import { CriticalWeddings } from "@/features/dashboard/components/CriticalWeddings";
import { RecentWeddings } from "@/features/dashboard/components/RecentWeddings";
import { UpcomingAppointments } from "@/features/dashboard/components/UpcomingAppointments";
import { UpcomingInstallments } from "@/features/dashboard/components/UpcomingInstallments";
import { getApiErrorInfo } from "@/api/error-utils";

import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { AlertCircle, ChevronLeft, ChevronRight } from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";

const WeddingMonthlyChart = lazy(
  () =>
    import("@/features/dashboard/components/WeddingMonthlyChart").then(
      (m) => ({ default: m.WeddingMonthlyChart }),
    ),
);

export default function DashboardPage() {
  const now = new Date();
  const [selectedYear, setSelectedYear] = useState(now.getFullYear());

  const { data, isLoading, error } = useWeddingsList();
  const { data: summaryData } = useDashboardSummary();

  if (isLoading) {
    return (
      <div className="flex-1 overflow-auto bg-zinc-50/30 dark:bg-zinc-950/30 min-h-screen">
        <div className="max-w-7xl mx-auto space-y-8 py-6">
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

  return (
    <div className="flex-1 overflow-auto bg-zinc-50/30 dark:bg-zinc-950/30 min-h-screen">
      <div className="max-w-7xl mx-auto space-y-8 animate-in fade-in duration-500 py-6 px-4">

        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h2 className="text-3xl font-bold tracking-tight text-violet-950 dark:text-violet-50">Dashboard Geral</h2>
            <p className="text-muted-foreground mt-1">Visão estratégica de todos os seus eventos.</p>
          </div>
          <div className="flex items-center gap-1 bg-background rounded-lg border shadow-sm border-violet-100 dark:border-violet-900/50">
            <Button
              variant="ghost"
              size="icon"
              className="h-9 w-9 text-violet-500 hover:text-violet-700"
              onClick={() => setSelectedYear((y) => y - 1)}
            >
              <ChevronLeft className="size-4" />
            </Button>
            <span className="text-sm font-medium min-w-[60px] text-center">
              {selectedYear}
            </span>
            <Button
              variant="ghost"
              size="icon"
              className="h-9 w-9 text-violet-500 hover:text-violet-700"
              onClick={() => setSelectedYear((y) => y + 1)}
            >
              <ChevronRight className="size-4" />
            </Button>
          </div>
        </div>

        {/* KPI Grid */}
        <StatsCards summary={summary} />

        {/* Critical Weddings Alert */}
        <CriticalWeddings weddings={summary?.critical_weddings ?? []} />

        {/* Main Content Grid */}
        <div className="grid gap-6 lg:grid-cols-3">
          <Suspense fallback={<Skeleton className="h-80 lg:col-span-2 rounded-xl shadow-sm" />}>
            <WeddingMonthlyChart weddings={weddingsArray} selectedYear={selectedYear} />
          </Suspense>
          <UpcomingAppointments />
        </div>

        <UpcomingInstallments />

        <div className="grid gap-6">
          <RecentWeddings weddings={weddingsArray} title="Próximos Casamentos" />
        </div>
      </div>
    </div>
  );
}
