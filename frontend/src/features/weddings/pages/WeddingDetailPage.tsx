import { useParams, Link } from "react-router-dom";
import { useMemo, useState } from "react";
import { useWeddingDetail } from "../hooks/useWeddingDetail";
import { TEMPLATE_MAP } from "../constants";
import { getWeddingsReadQueryKey, getWeddingsListQueryKey } from "@/api/generated/v1/endpoints/weddings/weddings";
import { useDashboardWedding, getDashboardWeddingQueryKey } from "@/api/generated/v1/endpoints/dashboard/dashboard";
import { WeddingDetailTabs } from "@/features/weddings/components/WeddingDetailTabs";
import { EditWeddingDialog } from "@/features/weddings/components/EditWeddingDialog";
import { useQueryClient } from "@tanstack/react-query";

import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Skeleton } from "@/components/ui/skeleton";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { AlertCircle, Calendar, MapPin, Pencil, Users } from "lucide-react";
import { getWeddingStatusBadgeStyle, getWeddingStatusLabel } from "@/features/weddings/utils/wedding-status";
import { cn } from "@/lib/utils";

export default function WeddingDetailPage() {
  const { uuid } = useParams<{ uuid: string }>();
  const queryClient = useQueryClient();
  const [editDialogOpen, setEditDialogOpen] = useState(false);

  const { data: response, isLoading, error } = useWeddingDetail(uuid!);

  const wedding = response?.data;

  const { data: dashboardResponse, isLoading: isLoadingDashboard } = useDashboardWedding(uuid!, {
    query: { enabled: !!uuid && !!wedding },
  });

  const weddingDate = wedding?.date;
  const overview = dashboardResponse?.data;

  const displayDate = useMemo(() => {
    if (!weddingDate) return "";
    const dateObj = new Date(weddingDate + "T00:00:00");
    const day = dateObj.getDate();
    const monthNames = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"];
    const month = monthNames[dateObj.getMonth()];
    const year = dateObj.getFullYear();
    return `${day} ${month} ${year}`;
  }, [weddingDate]);

  const formatBudget = (amount?: number | null) => {
    if (amount === undefined || amount === null) return "R$ —";
    if (amount >= 1000) {
      const value = amount / 1000;
      return `R$ ${value % 1 === 0 ? value : value.toFixed(1)}k`;
    }
    return `R$ ${amount}`;
  };

  const checklistPercentage = useMemo(() => {
    if (!overview || overview.tasks_total <= 0) return 0;
    return Math.round((overview.tasks_completed / overview.tasks_total) * 100);
  }, [overview]);

  const templateLabel = wedding?.template ? (TEMPLATE_MAP[wedding.template] ?? wedding.template) : null;
  const statusStyle = wedding ? getWeddingStatusBadgeStyle(wedding.status) : null;
  const statusLabel = wedding ? getWeddingStatusLabel(wedding.status) : "";

  if (!uuid) {
    return (
      <div className="flex flex-col gap-6 max-w-7xl mx-auto">
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>URL inválida</AlertTitle>
          <AlertDescription>
            Nenhum UUID de casamento foi encontrado na URL.
          </AlertDescription>
        </Alert>
        <div className="mt-4">
          <Button asChild variant="outline">
            <Link to="/weddings">
              Voltar para lista
            </Link>
          </Button>
        </div>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="flex flex-col gap-6 max-w-7xl mx-auto">
        <Skeleton className="h-8 w-64" />
        <Skeleton className="h-12 w-full" />
        <Skeleton className="h-100 w-full" />
      </div>
    );
  }
  if (error) {
    return (
      <div className="flex flex-col gap-6 max-w-7xl mx-auto">
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Erro ao carregar casamento</AlertTitle>
          <AlertDescription>
            {error.message ||
              "Não foi possível carregar os dados do casamento."}
          </AlertDescription>
        </Alert>
        <div className="mt-4">
          <Button asChild variant="outline">
            <Link to="/weddings">
              Voltar para lista
            </Link>
          </Button>
        </div>
      </div>
    );
  }

  if (!wedding) {
    return (
      <div className="flex flex-col gap-6 max-w-7xl mx-auto">
        <Alert>
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Casamento não encontrado</AlertTitle>
          <AlertDescription>
            O casamento solicitado não foi encontrado ou você não tem permissão
            para acessá-lo.
          </AlertDescription>
        </Alert>
        <div className="mt-4">
          <Button asChild variant="outline">
            <Link to="/weddings">
              Voltar para lista
            </Link>
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-6 max-w-7xl mx-auto animate-in fade-in duration-500">
      {/* Compact Profile Card */}
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
                onClick={() => setEditDialogOpen(true)}
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
                {isLoadingDashboard ? (
                  <Skeleton className="h-3 w-8" />
                ) : (
                  <span className="font-mono text-[10px] font-bold text-zinc-700 dark:text-zinc-300">
                    {checklistPercentage}%
                  </span>
                )}
              </div>
              {isLoadingDashboard ? (
                <Skeleton className="h-1.5 w-24 rounded-full" />
              ) : (
                <Progress value={checklistPercentage} className="h-1.5 w-24" />
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Tabs de conteúdo */}
      <WeddingDetailTabs wedding={wedding} />

      <EditWeddingDialog
        wedding={wedding}
        open={editDialogOpen}
        onOpenChange={setEditDialogOpen}
        onSuccess={() => {
          queryClient.invalidateQueries({ queryKey: getWeddingsReadQueryKey(uuid!) });
          queryClient.invalidateQueries({ queryKey: getWeddingsListQueryKey() });
          queryClient.invalidateQueries({ queryKey: getDashboardWeddingQueryKey(uuid!) });
          setEditDialogOpen(false);
        }}
      />
    </div>
  );
}
