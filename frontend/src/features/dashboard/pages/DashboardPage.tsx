import React, { useState } from "react";
import { useWeddingsList } from "@/api/generated/v1/endpoints/weddings/weddings";
import { StatsCards } from "@/features/dashboard/components/StatsCards";
import { RecentWeddings } from "@/features/dashboard/components/RecentWeddings";
import { WeddingMonthlyChart } from "@/features/dashboard/components/WeddingMonthlyChart";
import { UpcomingAppointments } from "@/features/dashboard/components/UpcomingAppointments";
import { getApiErrorInfo } from "@/api/error-utils";

import { Skeleton } from "@/components/ui/skeleton";
import { AlertCircle, Calendar as CalendarIcon } from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";

export default function DashboardPage() {
  const [activeFilter, setActiveFilter] = useState<string | null>(null);
  const { data, isLoading, error } = useWeddingsList();

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
            <Skeleton className="h-[400px] lg:col-span-2 rounded-xl shadow-sm" />
            <Skeleton className="h-[400px] rounded-xl shadow-sm" />
          </div>

          <Skeleton className="h-[350px] w-full rounded-xl shadow-sm" />
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

  const totalInDatabase = data?.data.count ?? 0;
  const weddingsArray = data?.data.items ?? [];
  const currentYear = new Date().getFullYear();

  // Filtragem simples baseada no activeFilter
  const filteredWeddings = weddingsArray.filter((wedding) => {
    if (!activeFilter || activeFilter === "all") return true;
    if (activeFilter === "month") {
      const date = new Date(wedding.date);
      return date.getMonth() === new Date().getMonth() &&
             date.getFullYear() === new Date().getFullYear();
    }
    // "guests" e "budget" são métricas globais, mostramos todos por enquanto
    return true;
  });

  return (
    <div className="flex-1 overflow-auto bg-zinc-50/30 dark:bg-zinc-950/30 min-h-screen">
      <div className="max-w-7xl mx-auto space-y-8 animate-in fade-in duration-500 py-6 px-4">

        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h2 className="text-3xl font-bold tracking-tight text-violet-950 dark:text-violet-50">Dashboard Geral</h2>
            <p className="text-muted-foreground mt-1">Visão estratégica de todos os seus eventos.</p>
          </div>
          <div className="flex items-center gap-3 bg-background px-4 py-2 rounded-lg border shadow-sm w-fit border-violet-100 dark:border-violet-900/50">
            <CalendarIcon className="size-4 text-violet-500" />
            <span className="text-sm font-medium">Ano de {currentYear}</span>
          </div>
        </div>

        {/* KPI Grid */}
        <StatsCards
          totalWeddings={totalInDatabase}
          activeFilter={activeFilter}
          onFilterChange={setActiveFilter}
        />

        {/* Main Content Grid */}
        <div className="grid gap-6 lg:grid-cols-3">
          {/* Chart Section */}
          <WeddingMonthlyChart weddings={weddingsArray} />

          {/* Side Column: Upcoming Events */}
          <UpcomingAppointments />
        </div>

        {/* Recent Activity Section */}
        <div className="grid gap-6">
          <RecentWeddings
            weddings={filteredWeddings}
            title={activeFilter === "month" ? "Casamentos deste Mês" : "Próximos Casamentos"}
          />
        </div>
      </div>
    </div>
  );
}
