import { DollarSign, AlertTriangle, FileText, Clock } from "lucide-react";
import type { DashboardSummaryOut } from "@/api/generated/v1/models/dashboardSummaryOut";
import { useWeddingsList } from "@/api/generated/v1/endpoints/weddings/weddings";
import {
  useFinancesExpensesList,
  useFinancesInstallmentsList,
} from "@/api/generated/v1/endpoints/finances/finances";
import { useSchedulerTasksList } from "@/api/generated/v1/endpoints/scheduler/scheduler";
import { useLogisticsContractsList } from "@/api/generated/v1/endpoints/logistics/logistics";
import { formatCurrencyBR, formatDateBR } from "@/lib/formatters";
import { MetricCard } from "./MetricCard";
import { DetailSheet } from "./DetailSheet";
import { formatWeddingName } from "../utils";

interface StatsCardsProps {
  summary?: DashboardSummaryOut;
}

export function StatsCards({ summary }: StatsCardsProps) {
  const parsedAmount = parseFloat(summary?.pending_installments_7d ?? "0");
  const pendingAmount = isNaN(parsedAmount) ? 0 : parsedAmount;
  const urgentTasksCount = summary?.urgent_tasks_count ?? 0;
  const parsedOverdueAmount = parseFloat(
    summary?.overdue_installments_amount ?? "0",
  );
  const overdueAmount = isNaN(parsedOverdueAmount) ? 0 : parsedOverdueAmount;
  const overdueCount = summary?.overdue_installments_count ?? 0;
  const pendingContractsCount = summary?.pending_contracts_count ?? 0;

  const { data: weddingsRes, isLoading: isLoadingWeddings } = useWeddingsList();
  const { data: expensesRes, isLoading: isLoadingExpenses } =
    useFinancesExpensesList({ limit: 100 });
  const { data: installmentsRes, isLoading: isLoadingInstallments } =
    useFinancesInstallmentsList({ limit: 100 });
  const { data: tasksRes, isLoading: isLoadingTasks } = useSchedulerTasksList({
    limit: 100,
  });
  const { data: contractsRes, isLoading: isLoadingContracts } =
    useLogisticsContractsList({ limit: 100 });

  const isSharedLoading =
    isLoadingWeddings ||
    isLoadingExpenses ||
    isLoadingInstallments ||
    isLoadingTasks ||
    isLoadingContracts;

  const weddingMap = (weddingsRes?.data?.items || []).reduce(
    (acc, w) => {
      acc[w.uuid] = formatWeddingName(w.bride_name, w.groom_name);
      return acc;
    },
    {} as Record<string, string>,
  );

  const expenseMap = (expensesRes?.data?.items || []).reduce(
    (acc, e) => {
      acc[e.uuid] = e.name;
      return acc;
    },
    {} as Record<string, string>,
  );

  const todayStr = new Date().toISOString().slice(0, 10);
  const next7Days = new Date();
  next7Days.setDate(next7Days.getDate() + 7);
  const next7DaysStr = next7Days.toISOString().slice(0, 10);

  const upcomingInstallmentsList = (
    installmentsRes?.data?.items || []
  ).filter(
    (inst) =>
      inst.status === "PENDING" &&
      inst.due_date >= todayStr &&
      inst.due_date <= next7DaysStr,
  );

  const overdueInstallmentsList = (
    installmentsRes?.data?.items || []
  ).filter(
    (inst) =>
      inst.status === "OVERDUE" ||
      (inst.status === "PENDING" && inst.due_date < todayStr),
  );

  const overdueTasksList = (tasksRes?.data?.items || []).filter(
    (task) =>
      !task.is_completed &&
      task.due_date != null &&
      task.due_date < todayStr,
  );

  const pendingContractsList = (contractsRes?.data?.items || []).filter(
    (contract) =>
      contract.status === "DRAFT" || contract.status === "PENDING",
  );

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
      {/* Card 1: Parcelas a Vencer */}
      <MetricCard
        label="Parcelas a Vencer (7d)"
        value={formatCurrencyBR(pendingAmount)}
        icon={<DollarSign />}
        severity="neutral"
        statusLabel="Próximos 7 dias"
        sheetTrigger={
          pendingAmount > 0 ? (
            <DetailSheet
              trigger={
                <button className="text-xs font-medium underline cursor-pointer text-aura-600 dark:text-aura-400 hover:text-aura-800 dark:hover:text-aura-300 bg-transparent border-0 p-0">
                  Ver Parcelas
                </button>
              }
              title="Parcelas a Vencer (7d)"
              description="Compromissos financeiros agendados para vencimento nos próximos 7 dias."
              icon={Clock}
              iconColor="text-aura-600"
              isLoading={isSharedLoading}
              isEmpty={upcomingInstallmentsList.length === 0}
              emptyMessage="Nenhuma parcela agendada para os próximos 7 dias."
            >
              {upcomingInstallmentsList.map((inst) => (
                <div
                  key={inst.uuid}
                  className="border border-zinc-100 dark:border-zinc-800/60 rounded-lg p-3 bg-zinc-50/50 dark:bg-zinc-900/40 flex justify-between items-center text-sm"
                >
                  <div>
                    <p className="font-semibold text-zinc-900 dark:text-zinc-100">
                      {expenseMap[inst.expense] || "Despesa"} (Parc. #
                      {inst.installment_number})
                    </p>
                    <p className="text-xs text-zinc-500 mt-0.5">
                      Vence em: {formatDateBR(inst.due_date)}
                    </p>
                    <p className="text-[11px] text-zinc-400 dark:text-zinc-500 mt-0.5 font-medium">
                      Casamento: {weddingMap[inst.wedding] || "N/A"}
                    </p>
                  </div>
                  <span className="font-mono font-bold text-zinc-900 dark:text-white">
                    {formatCurrencyBR(Number(inst.amount))}
                  </span>
                </div>
              ))}
            </DetailSheet>
          ) : null
        }
      >
        <div className="absolute right-0 top-0 w-24 h-24 rounded-bl-full -mr-4 -mt-4 transition-transform group-hover:scale-110 duration-300 bg-aura-500/5 dark:bg-aura-500/10" />
      </MetricCard>

      {/* Card 2: Parcelas Vencidas */}
      <MetricCard
        label="Parcelas Vencidas"
        value={formatCurrencyBR(overdueAmount)}
        icon={<DollarSign />}
        severity={overdueCount > 0 ? "danger" : "neutral"}
        statusLabel={
          overdueCount > 0
            ? `Ação Necessária: ${overdueCount} ${overdueCount === 1 ? "pendência" : "pendências"}`
            : "Nenhuma pendência"
        }
        sheetTrigger={
          overdueCount > 0 ? (
            <DetailSheet
              trigger={
                <button className="text-xs font-medium underline cursor-pointer text-destructive hover:text-red-700 dark:hover:text-red-400 bg-transparent border-0 p-0">
                  Ver Parcelas
                </button>
              }
              title="Parcelas Vencidas"
              description="Esta é a lista de parcelas que já venceram e precisam de atenção financeira."
              icon={DollarSign}
              iconColor="text-destructive"
              isLoading={isSharedLoading}
              isEmpty={overdueInstallmentsList.length === 0}
              emptyMessage="Nenhuma parcela vencida."
            >
              {overdueInstallmentsList.map((inst) => (
                <div
                  key={inst.uuid}
                  className="border border-red-100 dark:border-red-900/30 rounded-lg p-3 bg-red-50/30 dark:bg-red-900/10 flex justify-between items-center text-sm"
                >
                  <div>
                    <p className="font-semibold text-zinc-900 dark:text-zinc-100">
                      {expenseMap[inst.expense] || "Despesa"} (Parc. #
                      {inst.installment_number})
                    </p>
                    <p className="text-xs text-zinc-500 mt-0.5">
                      Venceu em: {formatDateBR(inst.due_date)}
                    </p>
                    <p className="text-[11px] text-zinc-600 dark:text-zinc-400 mt-0.5 font-medium">
                      Casamento: {weddingMap[inst.wedding] || "N/A"}
                    </p>
                  </div>
                  <span className="font-mono font-bold text-destructive">
                    {formatCurrencyBR(Number(inst.amount))}
                  </span>
                </div>
              ))}
            </DetailSheet>
          ) : null
        }
      >
        <div className="absolute right-0 top-0 w-24 h-24 rounded-bl-full -mr-4 -mt-4 transition-transform group-hover:scale-110 duration-300 bg-destructive/5 dark:bg-destructive/10" />
      </MetricCard>

      {/* Card 3: Tarefas Atrasadas */}
      <MetricCard
        label="Tarefas Atrasadas"
        value={urgentTasksCount}
        icon={<AlertTriangle />}
        severity={urgentTasksCount > 0 ? "danger" : "neutral"}
        statusLabel={
          urgentTasksCount > 0
            ? `Ação Necessária: ${urgentTasksCount} ${urgentTasksCount === 1 ? "pendência" : "pendências"}`
            : "Nenhuma pendência"
        }
        sheetTrigger={
          urgentTasksCount > 0 ? (
            <DetailSheet
              trigger={
                <button className="text-xs font-medium underline cursor-pointer text-destructive hover:text-red-700 dark:hover:text-red-400 bg-transparent border-0 p-0">
                  Ver Tarefas
                </button>
              }
              title="Tarefas Atrasadas"
              description="Lista de tarefas com prazos expirados que impedem o cronograma do casamento."
              icon={AlertTriangle}
              iconColor="text-destructive"
              isLoading={isSharedLoading}
              isEmpty={overdueTasksList.length === 0}
              emptyMessage="Nenhuma tarefa atrasada encontrada."
            >
              {overdueTasksList.map((task) => (
                <div
                  key={task.uuid}
                  className="border border-red-100 dark:border-red-900/30 rounded-lg p-4 bg-red-50/30 dark:bg-red-900/10 space-y-2 text-sm"
                >
                  <div className="flex items-start justify-between">
                    <p className="font-semibold text-zinc-900 dark:text-zinc-100">
                      {task.title}
                    </p>
                    <span className="text-[10px] bg-red-100 dark:bg-red-900/50 text-destructive px-2 py-0.5 rounded font-semibold">
                      Atrasada
                    </span>
                  </div>
                  {task.description && (
                    <p className="text-xs text-zinc-500">{task.description}</p>
                  )}
                  <p className="text-xs text-zinc-500 mt-0.5">
                    Prazo era:{" "}
                    {task.due_date ? formatDateBR(task.due_date) : "N/A"}
                  </p>
                  <p className="text-[11px] text-zinc-400 dark:text-zinc-500 font-medium">
                    Casamento: {weddingMap[task.wedding] || "N/A"}
                  </p>
                </div>
              ))}
            </DetailSheet>
          ) : null
        }
      >
        <div className="absolute right-0 top-0 w-24 h-24 rounded-bl-full -mr-4 -mt-4 transition-transform group-hover:scale-110 duration-300 bg-destructive/5 dark:bg-destructive/10" />
      </MetricCard>

      {/* Card 4: Contratos Pendentes */}
      <MetricCard
        label="Contratos Pendentes"
        value={pendingContractsCount}
        icon={<FileText />}
        severity={pendingContractsCount > 0 ? "warning" : "neutral"}
        statusLabel={
          pendingContractsCount > 0
            ? "Aguardando assinatura/sinal"
            : "Nenhum pendente"
        }
        sheetTrigger={
          pendingContractsCount > 0 ? (
            <DetailSheet
              trigger={
                <button className="text-xs font-medium underline cursor-pointer text-amber-600 dark:text-amber-400 hover:text-amber-800 dark:hover:text-amber-300 bg-transparent border-0 p-0">
                  Ver Contratos
                </button>
              }
              title="Contratos Pendentes"
              description="Lista de contratos com fornecedores em rascunho ou pendentes de assinatura/sinal."
              icon={FileText}
              iconColor="text-amber-600"
              isLoading={isSharedLoading}
              isEmpty={pendingContractsList.length === 0}
              emptyMessage="Nenhum contrato pendente."
            >
              {pendingContractsList.map((contract) => (
                <div
                  key={contract.uuid}
                  className="border border-amber-100 dark:border-amber-900/30 rounded-lg p-3 bg-amber-50/30 dark:bg-amber-900/10 flex justify-between items-center text-sm"
                >
                  <div>
                    <p className="font-semibold text-zinc-900 dark:text-zinc-100">
                      {contract.supplier_name || "Fornecedor"}
                    </p>
                    {contract.description && (
                      <p className="text-xs text-zinc-500 mt-0.5">
                        {contract.description}
                      </p>
                    )}
                    <p className="text-[11px] text-zinc-400 dark:text-zinc-500 mt-0.5 font-medium">
                      Casamento: {weddingMap[contract.wedding] || "N/A"}
                    </p>
                  </div>
                  <span className="font-mono font-bold text-amber-600 dark:text-amber-400">
                    {formatCurrencyBR(Number(contract.total_amount))}
                  </span>
                </div>
              ))}
            </DetailSheet>
          ) : null
        }
      >
        <div className="absolute right-0 top-0 w-24 h-24 rounded-bl-full -mr-4 -mt-4 transition-transform group-hover:scale-110 duration-300 bg-amber-500/5 dark:bg-amber-500/10" />
      </MetricCard>
    </div>
  );
}
