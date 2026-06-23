import { CalendarHeart, PiggyBank, CheckSquare, FileText, AlertTriangle, Clock } from "lucide-react";
import type { WeddingDashboardOut } from "@/api/generated/v1/models/weddingDashboardOut";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { formatCurrencyBR, formatDateBR } from "@/lib/formatters";
import { MetricCard } from "./MetricCard";
import { DetailSheet } from "./DetailSheet";
import { type Severity } from "../utils";

interface WeddingStatsCardsProps {
  data?: WeddingDashboardOut;
  isLoading?: boolean;
}

export function WeddingStatsCards({ data, isLoading }: WeddingStatsCardsProps) {
  if (isLoading) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
        {[...Array(4)].map((_, i) => (
          <Skeleton key={i} className="h-32 w-full rounded-xl" />
        ))}
      </div>
    );
  }

  const daysUntil = data?.days_until_wedding ?? 0;
  const budgetPct = data?.budget_percentage_used ?? 0;
  const tasksCompleted = data?.tasks_completed ?? 0;
  const tasksTotal = data?.tasks_total ?? 0;
  const contractsSigned = data?.contracts_signed ?? 0;
  const contractsTotal = data?.contracts_total ?? 0;
  const upcomingInstallments = data?.upcoming_installments ?? [];
  const urgentTasks = data?.urgent_tasks ?? [];

  const contractsPending = contractsTotal - contractsSigned;
  const tasksPending = tasksTotal - tasksCompleted;

  // Severity calculations (using original thresholds)
  const daysIsUrgent = daysUntil > 0 && daysUntil <= 30;
  const daysIsWarning = daysUntil > 30 && daysUntil <= 90;
  const daysSeverity: Severity = daysIsUrgent ? "danger" : daysIsWarning ? "warning" : "neutral";
  const budgetSeverity: Severity =
    budgetPct >= 90 ? "danger" : budgetPct >= 75 ? "warning" : "neutral";
  const tasksSeverity: Severity =
    tasksTotal === 0
      ? "neutral"
      : tasksCompleted === tasksTotal
        ? "success"
        : tasksCompleted < tasksTotal / 2
          ? "danger"
          : "warning";
  const contractsSeverity: Severity =
    contractsTotal === 0
      ? "neutral"
      : contractsSigned === contractsTotal
        ? "success"
        : contractsPending > contractsTotal / 2
          ? "danger"
          : "warning";

  // Status labels
  const daysStatusLabel =
    daysIsUrgent
      ? "⚠️ Urgente — menos de 30 dias"
      : daysIsWarning
        ? "📅 Menos de 90 dias"
        : `${daysUntil} dias restantes`;

  const budgetStatusLabel =
    budgetPct >= 90
      ? "Limite crítico"
      : budgetPct >= 75
        ? "Atenção ao budget"
        : "Dentro do orçamento";

  const tasksStatusLabel =
    tasksTotal > 0 && tasksCompleted === tasksTotal
      ? "✓ Todas concluídas"
      : `${tasksPending} pendente${tasksPending !== 1 ? "s" : ""}`;

  const contractsStatusLabel =
    contractsPending > 0
      ? `${contractsPending} pendente${contractsPending !== 1 ? "s" : ""} de assinatura`
      : contractsTotal === 0
        ? "Nenhum contrato"
        : "✓ Todos assinados";

  // Value display
  const daysValue = daysUntil > 0 ? daysUntil : "Hoje!";

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
      {/* Card 1: Dias até o Casamento */}
      <MetricCard
        label="Dias até o Casamento"
        value={daysValue}
        icon={<CalendarHeart />}
        severity={daysSeverity}
        statusLabel={daysStatusLabel}
      />

      {/* Card 2: Orçamento Utilizado */}
      <MetricCard
        label="Orçamento Utilizado"
        value={`${budgetPct.toFixed(1)}%`}
        icon={<PiggyBank />}
        severity={budgetSeverity}
        statusLabel={budgetStatusLabel}
        sheetTrigger={
          upcomingInstallments.length > 0 ? (
            <DetailSheet
              trigger={
                <Button variant="outline" size="sm" className="w-full">
                  <Clock className="mr-2 h-4 w-4" />
                  Ver Parcelas
                </Button>
              }
              title="Próximas Parcelas"
              description="Parcelas pendentes e vencidas nos próximos 30 dias."
              icon={Clock}
              iconColor="text-aura-500 dark:text-aura-400"
              isLoading={false}
              isEmpty={upcomingInstallments.length === 0}
              emptyMessage="Nenhuma parcela a vencer"
            >
              {upcomingInstallments.map((inst) => {
                const isOverdue = inst.status === "OVERDUE";
                return (
                  <div
                    key={String(inst.uuid)}
                    className={`border rounded-lg p-3 flex justify-between items-center text-sm ${
                      isOverdue
                        ? "border-red-100 dark:border-red-900/30 bg-red-50/30 dark:bg-red-900/10"
                        : "border-zinc-100 dark:border-zinc-800/60 bg-zinc-50/50 dark:bg-zinc-900/40"
                    }`}
                  >
                    <div>
                      <p className="font-semibold text-zinc-900 dark:text-zinc-100">
                        Parcela #{inst.installment_number}
                      </p>
                      <p className="text-xs text-zinc-500 mt-0.5">
                        {isOverdue ? "Venceu em:" : "Vence em:"}{" "}
                        {formatDateBR(String(inst.due_date))}
                      </p>
                      {isOverdue && (
                        <span className="text-[10px] text-destructive font-semibold">
                          Em atraso
                        </span>
                      )}
                    </div>
                    <span
                      className={`font-mono font-bold ${isOverdue ? "text-destructive" : "text-zinc-900 dark:text-white"}`}
                    >
                      R$ {formatCurrencyBR(Number(inst.amount))}
                    </span>
                  </div>
                );
              })}
            </DetailSheet>
          ) : undefined
        }
      >
        {/* Progress bar */}
        <div className="w-full bg-zinc-100 dark:bg-zinc-800 rounded-full h-1.5">
          <div
            className={`h-1.5 rounded-full transition-all duration-500 ${
              budgetSeverity === "danger"
                ? "bg-destructive"
                : budgetSeverity === "warning"
                  ? "bg-amber-500"
                  : "bg-aura-500"
            }`}
            style={{ width: `${Math.min(budgetPct, 100)}%` }}
          />
        </div>
      </MetricCard>

      {/* Card 3: Tarefas Concluídas */}
      <MetricCard
        label="Tarefas Concluídas"
        value={tasksCompleted}
        icon={<CheckSquare />}
        severity={tasksSeverity}
        statusLabel={tasksStatusLabel}
        sheetTrigger={
          urgentTasks.length > 0 ? (
            <DetailSheet
              trigger={
                <Button variant="outline" size="sm" className="w-full">
                  <AlertTriangle className="mr-2 h-4 w-4" />
                  Ver Urgentes
                </Button>
              }
              title="Tarefas Urgentes"
              description="Tarefas pendentes com prazo vencido ou sem data."
              icon={AlertTriangle}
              iconColor="text-amber-500 dark:text-amber-400"
              isLoading={false}
              isEmpty={urgentTasks.length === 0}
              emptyMessage="Nenhuma tarefa urgente"
            >
              {urgentTasks.map((task) => (
                <div
                  key={String(task.uuid)}
                  className="border border-amber-100 dark:border-amber-900/30 rounded-lg p-3 bg-amber-50/30 dark:bg-amber-900/10 text-sm"
                >
                  <p className="font-semibold text-zinc-900 dark:text-zinc-100">
                    {task.title}
                  </p>
                  <p className="text-xs text-zinc-500 mt-0.5">
                    {task.due_date
                      ? `Prazo: ${formatDateBR(String(task.due_date))}`
                      : "Sem data definida"}
                  </p>
                </div>
              ))}
            </DetailSheet>
          ) : undefined
        }
      >
        <div className="flex items-baseline gap-1 mb-2">
          <span className="text-base text-muted-foreground">/ {tasksTotal}</span>
        </div>
        {/* Progress bar */}
        <div className="w-full bg-zinc-100 dark:bg-zinc-800 rounded-full h-1.5">
          <div
            className={`h-1.5 rounded-full transition-all duration-500 ${
              tasksTotal > 0 && tasksCompleted === tasksTotal
                ? "bg-success"
                : "bg-amber-500"
            }`}
            style={{
              width:
                tasksTotal > 0
                  ? `${(tasksCompleted / tasksTotal) * 100}%`
                  : "0%",
            }}
          />
        </div>
      </MetricCard>

      {/* Card 4: Contratos Assinados */}
      <MetricCard
        label="Contratos Assinados"
        value={contractsSigned}
        icon={<FileText />}
        severity={contractsSeverity}
        statusLabel={contractsStatusLabel}
      >
        <div className="flex items-baseline gap-1 mb-2">
          <span className="text-base text-muted-foreground">/ {contractsTotal}</span>
        </div>
        {/* Progress bar */}
        <div className="w-full bg-zinc-100 dark:bg-zinc-800 rounded-full h-1.5">
          <div
            className={`h-1.5 rounded-full transition-all duration-500 ${
              contractsTotal > 0 && contractsSigned === contractsTotal
                ? "bg-success"
                : "bg-amber-500"
            }`}
            style={{
              width:
                contractsTotal > 0
                  ? `${(contractsSigned / contractsTotal) * 100}%`
                  : "0%",
            }}
          />
        </div>
      </MetricCard>
    </div>
  );
}
