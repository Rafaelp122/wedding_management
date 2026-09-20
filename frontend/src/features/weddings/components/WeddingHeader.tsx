import { memo } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import type { WeddingOut } from "@/api/generated/v1/models/weddingOut";
import {
  useWeddingsReopen,
  getWeddingsReadQueryKey,
  getWeddingsListQueryKey,
} from "@/api/generated/v1/endpoints/weddings/weddings";
import { getDashboardWeddingQueryKey } from "@/api/generated/v1/endpoints/dashboard/dashboard";
import { getApiErrorInfo } from "@/api/error-utils";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Skeleton } from "@/components/ui/skeleton";
import { Calendar, CheckCircle2, MapPin, Pencil, RotateCcw, Users, XCircle } from "lucide-react";
import { getWeddingStatusBadgeStyle, getWeddingStatusLabel } from "@/features/weddings/utils/wedding-status";
import { cn } from "@/lib/utils";
import { TEMPLATE_MAP } from "../constants";

interface WeddingHeaderProps {
  wedding: WeddingOut;
  displayDate: string;
  checklistPercentage: number;
  isLoadingOverview?: boolean;
  onEditClick: () => void;
  onCompleteClick?: () => void;
  onCancelClick?: () => void;
  onReopenClick?: () => void;
}

export const WeddingHeader = memo(function WeddingHeader({
  wedding,
  displayDate,
  checklistPercentage,
  isLoadingOverview = false,
  onEditClick,
  onCompleteClick,
  onCancelClick,
  onReopenClick,
}: WeddingHeaderProps) {
  const queryClient = useQueryClient();
  const { mutate: reopenWedding, isPending: isReopening } = useWeddingsReopen();

  const templateLabel = wedding.template ? (TEMPLATE_MAP[wedding.template] ?? wedding.template) : null;
  const statusStyle = getWeddingStatusBadgeStyle(wedding.status);
  const statusLabel = getWeddingStatusLabel(wedding.status);

  const formatBudget = (amount?: number | string | null) => {
    if (amount === undefined || amount === null || amount === "") return "R$ —";
    const num = typeof amount === "number" ? amount : Number.parseFloat(amount);
    if (Number.isNaN(num)) return "R$ —";
    if (num >= 1000) {
      const value = num / 1000;
      return `R$ ${value % 1 === 0 ? value : value.toFixed(1)}k`;
    }
    return `R$ ${num}`;
  };

  const canComplete = Boolean(wedding.can_complete);
  const canReopen =
    wedding.status === "CANCELED" ||
    (wedding.allowed_transitions?.includes("IN_PROGRESS") ?? false);

  const handleReopen = () => {
    if (onReopenClick) {
      onReopenClick();
      return;
    }
    reopenWedding(
      { uuid: wedding.uuid },
      {
        onSuccess: () => {
          toast.success("Casamento reaberto com sucesso!");
          queryClient.invalidateQueries({ queryKey: getWeddingsReadQueryKey(wedding.uuid) });
          queryClient.invalidateQueries({ queryKey: getWeddingsListQueryKey() });
          queryClient.invalidateQueries({ queryKey: getDashboardWeddingQueryKey(wedding.uuid) });
        },
        onError: (err) => {
          const { message } = getApiErrorInfo(err, "Erro ao reabrir casamento.");
          toast.error(message);
        },
      },
    );
  };

  return (
    <div className="bg-white dark:bg-[#18181B] p-4 rounded-xl border border-zinc-200 dark:border-zinc-800 shadow-sm relative overflow-hidden">
      {/* Fundo decorativo de canto */}
      <div className="absolute right-0 top-0 w-16 h-16 bg-primary/5 rounded-bl-full pointer-events-none" />

      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 relative z-10">
        {/* Bloco da esquerda: Nomes, Categoria, Data, Local e Convidados */}
        <div className="flex flex-col gap-1.5">
          {/* Linha 1: Nomes, badge de Estilo + badge de Status + botão de Edição */}
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
            {wedding.status === "IN_PROGRESS" && onCompleteClick && (
              <Button
                variant="ghost"
                size="icon"
                className={cn(
                  "h-7 w-7 rounded-full cursor-pointer transition-colors",
                  canComplete
                    ? "text-emerald-600 hover:text-emerald-700 hover:bg-emerald-50 dark:hover:bg-emerald-950/30"
                    : "text-zinc-300 dark:text-zinc-600 cursor-not-allowed",
                )}
                onClick={canComplete ? onCompleteClick : undefined}
                disabled={!canComplete}
                title={
                  canComplete
                    ? "Concluir casamento"
                    : "O casamento só pode ser concluído na data do evento ou posterior"
                }
              >
                <CheckCircle2 className="h-3.5 w-3.5" />
              </Button>
            )}
            {canReopen && (
              <Button
                variant="ghost"
                size="icon"
                className="h-7 w-7 text-amber-600 hover:text-amber-700 hover:bg-amber-50 dark:hover:bg-amber-950/30 rounded-full cursor-pointer transition-colors"
                onClick={handleReopen}
                disabled={isReopening}
                title="Reabrir casamento"
              >
                <RotateCcw className="h-3.5 w-3.5" />
              </Button>
            )}
            {wedding.status === "IN_PROGRESS" && onCancelClick && (
              <Button
                variant="ghost"
                size="icon"
                className="h-7 w-7 text-rose-500 hover:text-rose-600 hover:bg-rose-50 dark:hover:bg-rose-950/30 rounded-full cursor-pointer transition-colors"
                onClick={onCancelClick}
                title="Cancelar casamento"
              >
                <XCircle className="h-3.5 w-3.5" />
              </Button>
            )}
          </div>

          {/* Linha 2: Data, Endereço e Convidados consolidados */}
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

        {/* Bloco da direita: Barra financeira compacta + indicador do Checklist em linha */}
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
