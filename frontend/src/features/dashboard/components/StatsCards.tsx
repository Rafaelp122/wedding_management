import { DollarSign, AlertTriangle, FileText, Clock, type LucideIcon } from "lucide-react";
import type { DashboardSummaryOut } from "@/api/generated/v1/models/dashboardSummaryOut";
import type { DashboardInstallmentDetailOut } from "@/api/generated/v1/models/dashboardInstallmentDetailOut";
import type { DashboardTaskDetailOut } from "@/api/generated/v1/models/dashboardTaskDetailOut";
import type { DashboardContractDetailOut } from "@/api/generated/v1/models/dashboardContractDetailOut";
import { formatCurrencyBR, formatDateBR } from "@/lib/formatters";
import { MetricCard } from "./MetricCard";
import { DetailSheet } from "./DetailSheet";

export interface InstallmentsDetailSheetProps {
  trigger: React.ReactNode;
  title: string;
  description: string;
  icon: LucideIcon;
  iconColor: string;
  emptyMessage: string;
  isOverdueVariant?: boolean;
  installments: DashboardInstallmentDetailOut[];
}

export function InstallmentsDetailSheet({
  trigger,
  title,
  description,
  icon,
  iconColor,
  emptyMessage,
  isOverdueVariant = false,
  installments,
}: InstallmentsDetailSheetProps) {
  return (
    <DetailSheet
      trigger={trigger}
      title={title}
      description={description}
      icon={icon}
      iconColor={iconColor}
      isLoading={false}
      isEmpty={installments.length === 0}
      emptyMessage={emptyMessage}
    >
      {installments.map((inst) => (
        <div
          key={inst.uuid}
          className={
            isOverdueVariant
              ? "border border-red-100 dark:border-red-900/30 rounded-lg p-3 bg-red-50/30 dark:bg-red-900/10 flex justify-between items-center text-sm"
              : "border border-zinc-100 dark:border-zinc-800/60 rounded-lg p-3 bg-zinc-50/50 dark:bg-zinc-900/40 flex justify-between items-center text-sm"
          }
        >
          <div>
            <p className="font-semibold text-zinc-900 dark:text-zinc-100">
              Parc. #{inst.installment_number}
            </p>
            <p className="text-xs text-zinc-500 mt-0.5">
              {isOverdueVariant ? "Venceu em:" : "Vence em:"} {formatDateBR(inst.due_date)}
            </p>
            <p
              className={
                isOverdueVariant
                  ? "text-[11px] text-zinc-600 dark:text-zinc-400 mt-0.5 font-medium"
                  : "text-[11px] text-zinc-400 dark:text-zinc-500 mt-0.5 font-medium"
              }
            >
              Casamento: {inst.wedding_name || "N/A"}
            </p>
          </div>
          <span
            className={
              isOverdueVariant
                ? "font-mono font-bold text-destructive"
                : "font-mono font-bold text-zinc-900 dark:text-white"
            }
          >
            {formatCurrencyBR(Number(inst.amount))}
          </span>
        </div>
      ))}
    </DetailSheet>
  );
}

export interface TasksDetailSheetProps {
  trigger: React.ReactNode;
  tasks: DashboardTaskDetailOut[];
}

export function TasksDetailSheet({ trigger, tasks }: TasksDetailSheetProps) {
  return (
    <DetailSheet
      trigger={trigger}
      title="Tarefas Atrasadas"
      description="Lista de tarefas com prazos expirados que impedem o cronograma do casamento."
      icon={AlertTriangle}
      iconColor="text-destructive"
      isLoading={false}
      isEmpty={tasks.length === 0}
      emptyMessage="Nenhuma tarefa atrasada encontrada."
    >
      {tasks.map((task) => (
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
          <p className="text-xs text-zinc-500 mt-0.5">
            Prazo era: {task.due_date ? formatDateBR(task.due_date) : "N/A"}
          </p>
          <p className="text-[11px] text-zinc-400 dark:text-zinc-500 font-medium">
            Casamento: {task.wedding_name || "N/A"}
          </p>
        </div>
      ))}
    </DetailSheet>
  );
}

export interface ContractsDetailSheetProps {
  trigger: React.ReactNode;
  contracts: DashboardContractDetailOut[];
}

export function ContractsDetailSheet({ trigger, contracts }: ContractsDetailSheetProps) {
  return (
    <DetailSheet
      trigger={trigger}
      title="Contratos Pendentes"
      description="Lista de contratos com fornecedores em rascunho ou pendentes de assinatura/sinal."
      icon={FileText}
      iconColor="text-amber-600"
      isLoading={false}
      isEmpty={contracts.length === 0}
      emptyMessage="Nenhum contrato pendente."
    >
      {contracts.map((contract) => (
        <div
          key={contract.uuid}
          className="border border-amber-100 dark:border-amber-900/30 rounded-lg p-3 bg-amber-50/30 dark:bg-amber-900/10 flex justify-between items-center text-sm"
        >
          <div>
            <p className="font-semibold text-zinc-900 dark:text-zinc-100">
              {contract.supplier_name || "Fornecedor"}
            </p>
            <p className="text-[11px] text-zinc-400 dark:text-zinc-500 mt-0.5 font-medium">
              Casamento: {contract.wedding_name || "N/A"}
            </p>
          </div>
          <span className="font-mono font-bold text-amber-600 dark:text-amber-400">
            {formatCurrencyBR(Number(contract.total_amount))}
          </span>
        </div>
      ))}
    </DetailSheet>
  );
}

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

  const upcomingInstallments = summary?.upcoming_installments ?? [];
  const overdueInstallments = summary?.overdue_installments ?? [];
  const urgentTasks = summary?.urgent_tasks ?? [];
  const pendingContracts = summary?.pending_contracts ?? [];

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
            <InstallmentsDetailSheet
              trigger={
                <button className="text-xs font-medium underline cursor-pointer text-aura-600 dark:text-aura-400 hover:text-aura-800 dark:hover:text-aura-300 bg-transparent border-0 p-0">
                  Ver Parcelas
                </button>
              }
              title="Parcelas a Vencer (7d)"
              description="Compromissos financeiros agendados para vencimento nos próximos 7 dias."
              icon={Clock}
              iconColor="text-aura-600"
              emptyMessage="Nenhuma parcela agendada para os próximos 7 dias."
              installments={upcomingInstallments}
            />
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
            <InstallmentsDetailSheet
              trigger={
                <button className="text-xs font-medium underline cursor-pointer text-destructive hover:text-red-700 dark:hover:text-red-400 bg-transparent border-0 p-0">
                  Ver Parcelas
                </button>
              }
              title="Parcelas Vencidas"
              description="Esta é a lista de parcelas que já venceram e precisam de atenção financeira."
              icon={DollarSign}
              iconColor="text-destructive"
              isOverdueVariant
              emptyMessage="Nenhuma parcela vencida."
              installments={overdueInstallments}
            />
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
            <TasksDetailSheet
              trigger={
                <button className="text-xs font-medium underline cursor-pointer text-destructive hover:text-red-700 dark:hover:text-red-400 bg-transparent border-0 p-0">
                  Ver Tarefas
                </button>
              }
              tasks={urgentTasks}
            />
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
            <ContractsDetailSheet
              trigger={
                <button className="text-xs font-medium underline cursor-pointer text-amber-600 dark:text-amber-400 hover:text-amber-800 dark:hover:text-amber-300 bg-transparent border-0 p-0">
                  Ver Contratos
                </button>
              }
              contracts={pendingContracts}
            />
          ) : null
        }
      >
        <div className="absolute right-0 top-0 w-24 h-24 rounded-bl-full -mr-4 -mt-4 transition-transform group-hover:scale-110 duration-300 bg-amber-500/5 dark:bg-amber-500/10" />
      </MetricCard>
    </div>
  );
}
