import { DollarSign, AlertTriangle, FileText, Clock } from "lucide-react";
import type { DashboardSummaryOut } from "@/api/generated/v1/models/dashboardSummaryOut";
import { useWeddingsList } from "@/api/generated/v1/endpoints/weddings/weddings";
import {
  useFinancesExpensesList,
  useFinancesInstallmentsList,
} from "@/api/generated/v1/endpoints/finances/finances";
import { useSchedulerTasksList } from "@/api/generated/v1/endpoints/scheduler/scheduler";
import { useLogisticsContractsList } from "@/api/generated/v1/endpoints/logistics/logistics";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet";

interface StatsCardsProps {
  summary?: DashboardSummaryOut;
}

const formatCurrency = (value: number) =>
  new Intl.NumberFormat("pt-BR", {
    style: "currency",
    currency: "BRL",
  }).format(value);

const formatDate = (dateStr: string) => {
  try {
    return new Date(dateStr).toLocaleDateString("pt-BR", { timeZone: "UTC" });
  } catch {
    return dateStr;
  }
};

export function StatsCards({ summary }: StatsCardsProps) {
  const parsedAmount = parseFloat(summary?.pending_installments_7d ?? "0");
  const pendingAmount = isNaN(parsedAmount) ? 0 : parsedAmount;
  const urgentTasksCount = summary?.urgent_tasks_count ?? 0;
  const parsedOverdueAmount = parseFloat(summary?.overdue_installments_amount ?? "0");
  const overdueAmount = isNaN(parsedOverdueAmount) ? 0 : parsedOverdueAmount;
  const overdueCount = summary?.overdue_installments_count ?? 0;
  const pendingContractsCount = summary?.pending_contracts_count ?? 0;

  // Fetch lists to dynamically render details inside the sidebars
  const { data: weddingsRes, isLoading: isLoadingWeddings } = useWeddingsList();
  const { data: expensesRes, isLoading: isLoadingExpenses } = useFinancesExpensesList({ limit: 100 });
  const { data: installmentsRes, isLoading: isLoadingInstallments } = useFinancesInstallmentsList({ limit: 100 });
  const { data: tasksRes, isLoading: isLoadingTasks } = useSchedulerTasksList({ limit: 100 });
  const { data: contractsRes, isLoading: isLoadingContracts } = useLogisticsContractsList({ limit: 100 });

  const isSharedLoading =
    isLoadingWeddings ||
    isLoadingExpenses ||
    isLoadingInstallments ||
    isLoadingTasks ||
    isLoadingContracts;

  // Create lookup maps for names
  const weddingMap = (weddingsRes?.data?.items || []).reduce((acc, w) => {
    acc[w.uuid] = `${w.bride_name} & ${w.groom_name}`;
    return acc;
  }, {} as Record<string, string>);

  const expenseMap = (expensesRes?.data?.items || []).reduce((acc, e) => {
    acc[e.uuid] = e.name;
    return acc;
  }, {} as Record<string, string>);

  const todayStr = new Date().toISOString().slice(0, 10);
  const next7Days = new Date();
  next7Days.setDate(next7Days.getDate() + 7);
  const next7DaysStr = next7Days.toISOString().slice(0, 10);

  // Filters for lists
  const upcomingInstallmentsList = (installmentsRes?.data?.items || []).filter(
    (inst) =>
      inst.status === "PENDING" &&
      inst.due_date >= todayStr &&
      inst.due_date <= next7DaysStr
  );

  const overdueInstallmentsList = (installmentsRes?.data?.items || []).filter(
    (inst) =>
      inst.status === "OVERDUE" ||
      (inst.status === "PENDING" && inst.due_date < todayStr)
  );

  const overdueTasksList = (tasksRes?.data?.items || []).filter(
    (task) => !task.is_completed && task.due_date != null && task.due_date < todayStr
  );

  const pendingContractsList = (contractsRes?.data?.items || []).filter(
    (contract) =>
      contract.status === "DRAFT" || contract.status === "PENDING"
  );

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
      {/* Card 1: Financeiro / Parcelas a Vencer */}
      <div className="bg-card p-5 rounded-xl border border-zinc-200 dark:border-zinc-800 shadow-soft relative overflow-hidden group">
        <div className="absolute right-0 top-0 w-24 h-24 bg-aura-500/5 dark:bg-aura-500/10 rounded-bl-full -mr-4 -mt-4 transition-transform group-hover:scale-110 duration-300"></div>
        <div className="flex justify-between items-start mb-4 relative z-10">
          <div>
            <p className="text-sm font-medium text-zinc-500 dark:text-zinc-400">Parcelas a Vencer (7d)</p>
            <h3 className="font-mono text-2xl font-semibold text-zinc-900 dark:text-white mt-1">
              {formatCurrency(pendingAmount)}
            </h3>
          </div>
          <div className="w-10 h-10 rounded-lg bg-aura-50 dark:bg-aura-900/30 flex items-center justify-center text-aura-600 dark:text-aura-400 border border-aura-100 dark:border-aura-800/50">
            <DollarSign className="w-5 h-5" />
          </div>
        </div>
        <div className="flex items-center justify-between mt-4 relative z-10">
          <div className="flex items-center text-xs font-medium text-success bg-success/10 w-max px-2 py-1 rounded">
            <span>Próximos 7 dias</span>
          </div>
          {pendingAmount > 0 && (
            <Sheet>
              <SheetTrigger asChild>
                <button className="text-xs font-medium text-aura-600 dark:text-aura-400 underline cursor-pointer hover:text-aura-800 dark:hover:text-aura-300 bg-transparent border-0 p-0">
                  Ver Parcelas
                </button>
              </SheetTrigger>
              <SheetContent side="right" className="sm:max-w-md bg-white dark:bg-zinc-900 border-l border-zinc-200 dark:border-zinc-800 shadow-lg text-zinc-900 dark:text-zinc-100">
                <SheetHeader>
                  <SheetTitle className="flex items-center gap-2 text-aura-600 dark:text-aura-400 font-bold text-lg">
                    <Clock className="w-5 h-5" />
                    Parcelas a Vencer (7d)
                  </SheetTitle>
                  <SheetDescription className="text-zinc-500 dark:text-zinc-400 text-sm">
                    Compromissos financeiros agendados para vencimento nos próximos 7 dias.
                  </SheetDescription>
                </SheetHeader>
                <div className="mt-6 space-y-3">
                  {isSharedLoading ? (
                    <div className="space-y-2">
                      <Skeleton className="h-14 w-full" />
                      <Skeleton className="h-14 w-full" />
                    </div>
                  ) : upcomingInstallmentsList.length === 0 ? (
                    <p className="text-sm text-zinc-500 text-center py-4">Nenhuma parcela agendada para os próximos 7 dias.</p>
                  ) : (
                    upcomingInstallmentsList.map((inst) => (
                      <div key={inst.uuid} className="border border-zinc-100 dark:border-zinc-800/60 rounded-lg p-3 bg-zinc-50/50 dark:bg-zinc-900/40 flex justify-between items-center text-sm">
                        <div>
                          <p className="font-semibold text-zinc-900 dark:text-zinc-100">
                            {expenseMap[inst.expense] || "Despesa"} (Parc. #{inst.installment_number})
                          </p>
                          <p className="text-xs text-zinc-500 mt-0.5">Vence em: {formatDate(inst.due_date)}</p>
                          <p className="text-[11px] text-zinc-400 dark:text-zinc-500 mt-0.5 font-medium">
                            Casamento: {weddingMap[inst.wedding] || "N/A"}
                          </p>
                        </div>
                        <span className="font-mono font-bold text-zinc-900 dark:text-white">
                          {formatCurrency(Number(inst.amount))}
                        </span>
                      </div>
                    ))
                  )}
                </div>
              </SheetContent>
            </Sheet>
          )}
        </div>
      </div>

      {/* Card 2: Parcelas Vencidas (Danger Focus - Dynamic) */}
      <div className={`bg-card p-5 rounded-xl shadow-soft relative overflow-hidden group border transition-all ${
        overdueCount > 0
          ? "border-red-200 dark:border-red-900/30"
          : "border-zinc-200 dark:border-zinc-800"
      }`}>
        <div className={`absolute right-0 top-0 w-24 h-24 rounded-bl-full -mr-4 -mt-4 transition-transform group-hover:scale-110 duration-300 ${
          overdueCount > 0
            ? "bg-destructive/5 dark:bg-destructive/10"
            : "bg-aura-500/5 dark:bg-aura-500/10"
        }`}></div>
        <div className="flex justify-between items-start mb-4 relative z-10">
          <div>
            <p className="text-sm font-medium text-zinc-500 dark:text-zinc-400">Parcelas Vencidas</p>
            <h3 className={`font-mono text-2xl font-semibold mt-1 ${
              overdueCount > 0 ? "text-destructive" : "text-zinc-900 dark:text-white"
            }`}>
              {formatCurrency(overdueAmount)}
            </h3>
          </div>
          <div className={`w-10 h-10 rounded-lg flex items-center justify-center border transition-all ${
            overdueCount > 0
              ? "bg-red-50 dark:bg-red-900/30 text-destructive border-red-100 dark:border-red-800/50"
              : "bg-zinc-50 dark:bg-zinc-800 text-zinc-400 border-zinc-100 dark:border-zinc-700"
          }`}>
            <DollarSign className="w-5 h-5" />
          </div>
        </div>
        
        <div className="flex items-center justify-between mt-4 relative z-10">
          <div className={`flex items-center text-xs font-medium w-max px-2 py-1 rounded border ${
            overdueCount > 0
              ? "bg-red-50 dark:bg-red-900/20 text-destructive border-red-100 dark:border-red-800/30"
              : "bg-zinc-100 dark:bg-zinc-800 text-zinc-500 dark:text-zinc-400 border-transparent"
          }`}>
            <span>{overdueCount > 0 ? `Ação Necessária: ${overdueCount} pendência${overdueCount > 1 ? "s" : ""}` : "Nenhuma pendência"}</span>
          </div>
          {overdueCount > 0 && (
            <Sheet>
              <SheetTrigger asChild>
                <button className="text-xs font-medium text-destructive underline cursor-pointer hover:text-red-700 dark:hover:text-red-400 bg-transparent border-0 p-0">
                  Ver Parcelas
                </button>
              </SheetTrigger>
              <SheetContent side="right" className="sm:max-w-md bg-white dark:bg-zinc-900 border-l border-zinc-200 dark:border-zinc-800 shadow-lg text-zinc-900 dark:text-zinc-100">
                <SheetHeader>
                  <SheetTitle className="flex items-center gap-2 text-destructive font-bold text-lg">
                    <DollarSign className="w-5 h-5" />
                    Parcelas Vencidas
                  </SheetTitle>
                  <SheetDescription className="text-zinc-500 dark:text-zinc-400 text-sm">
                    Esta é a lista de parcelas que já venceram e precisam de atenção financeira.
                  </SheetDescription>
                </SheetHeader>
                <div className="mt-6 space-y-3">
                  {isSharedLoading ? (
                    <div className="space-y-2">
                      <Skeleton className="h-14 w-full" />
                      <Skeleton className="h-14 w-full" />
                    </div>
                  ) : overdueInstallmentsList.length === 0 ? (
                    <p className="text-sm text-zinc-500 text-center py-4">Nenhuma parcela vencida.</p>
                  ) : (
                    overdueInstallmentsList.map((inst) => (
                      <div key={inst.uuid} className="border border-red-100 dark:border-red-900/30 rounded-lg p-3 bg-red-50/30 dark:bg-red-900/10 flex justify-between items-center text-sm">
                        <div>
                          <p className="font-semibold text-zinc-900 dark:text-zinc-100">
                            {expenseMap[inst.expense] || "Despesa"} (Parc. #{inst.installment_number})
                          </p>
                          <p className="text-xs text-zinc-500 mt-0.5">Venceu em: {formatDate(inst.due_date)}</p>
                          <p className="text-[11px] text-zinc-600 dark:text-zinc-400 mt-0.5 font-medium">
                            Casamento: {weddingMap[inst.wedding] || "N/A"}
                          </p>
                        </div>
                        <span className="font-mono font-bold text-destructive">
                          {formatCurrency(Number(inst.amount))}
                        </span>
                      </div>
                    ))
                  )}
                </div>
              </SheetContent>
            </Sheet>
          )}
        </div>
      </div>

      {/* Card 3: Tarefas Atrasadas (Danger Focus - Dynamic) */}
      <div className={`bg-card p-5 rounded-xl shadow-soft relative overflow-hidden group border transition-all ${
        urgentTasksCount > 0
          ? "border-red-200 dark:border-red-900/30"
          : "border-zinc-200 dark:border-zinc-800"
      }`}>
        <div className={`absolute right-0 top-0 w-24 h-24 rounded-bl-full -mr-4 -mt-4 transition-transform group-hover:scale-110 duration-300 ${
          urgentTasksCount > 0
            ? "bg-destructive/5 dark:bg-destructive/10"
            : "bg-aura-500/5 dark:bg-aura-500/10"
        }`}></div>
        <div className="flex justify-between items-start mb-4 relative z-10">
          <div>
            <p className="text-sm font-medium text-zinc-500 dark:text-zinc-400">Tarefas Atrasadas</p>
            <h3 className={`font-mono text-2xl font-semibold mt-1 ${
              urgentTasksCount > 0 ? "text-destructive" : "text-zinc-900 dark:text-white"
            }`}>
              {urgentTasksCount}
            </h3>
          </div>
          <div className={`w-10 h-10 rounded-lg flex items-center justify-center border transition-all ${
            urgentTasksCount > 0
              ? "bg-red-50 dark:bg-red-900/30 text-destructive border-red-100 dark:border-red-800/50"
              : "bg-zinc-50 dark:bg-zinc-800 text-zinc-400 border-zinc-100 dark:border-zinc-700"
          }`}>
            <AlertTriangle className="w-5 h-5" />
          </div>
        </div>
        
        <div className="flex items-center justify-between mt-4 relative z-10">
          <div className={`flex items-center text-xs font-medium w-max px-2 py-1 rounded border ${
            urgentTasksCount > 0
              ? "bg-red-50 dark:bg-red-900/20 text-destructive border-red-100 dark:border-red-800/30"
              : "bg-zinc-100 dark:bg-zinc-800 text-zinc-500 dark:text-zinc-400 border-transparent"
          }`}>
            <span>{urgentTasksCount > 0 ? `Ação Necessária: ${urgentTasksCount} pendência${urgentTasksCount > 1 ? "s" : ""}` : "Nenhuma pendência"}</span>
          </div>
          {urgentTasksCount > 0 && (
            <Sheet>
              <SheetTrigger asChild>
                <button className="text-xs font-medium text-destructive underline cursor-pointer hover:text-red-700 dark:hover:text-red-400 bg-transparent border-0 p-0">
                  Ver Tarefas
                </button>
              </SheetTrigger>
              <SheetContent side="right" className="sm:max-w-md bg-white dark:bg-zinc-900 border-l border-zinc-200 dark:border-zinc-800 shadow-lg text-zinc-900 dark:text-zinc-100">
                <SheetHeader>
                  <SheetTitle className="flex items-center gap-2 text-destructive font-bold text-lg">
                    <AlertTriangle className="w-5 h-5" />
                    Tarefas Atrasadas
                  </SheetTitle>
                  <SheetDescription className="text-zinc-500 dark:text-zinc-400 text-sm">
                    Lista de tarefas com prazos expirados que impedem o cronograma do casamento.
                  </SheetDescription>
                </SheetHeader>
                <div className="mt-6 space-y-4">
                  {isSharedLoading ? (
                    <div className="space-y-2">
                      <Skeleton className="h-14 w-full" />
                      <Skeleton className="h-14 w-full" />
                    </div>
                  ) : overdueTasksList.length === 0 ? (
                    <p className="text-sm text-zinc-500 text-center py-4">Nenhuma tarefa atrasada encontrada.</p>
                  ) : (
                    overdueTasksList.map((task) => (
                      <div key={task.uuid} className="border border-red-100 dark:border-red-900/30 rounded-lg p-4 bg-red-50/30 dark:bg-red-900/10 space-y-2 text-sm">
                        <div className="flex items-start justify-between">
                          <p className="font-semibold text-zinc-900 dark:text-zinc-100">{task.title}</p>
                          <span className="text-[10px] bg-red-100 dark:bg-red-900/50 text-destructive px-2 py-0.5 rounded font-semibold">Atrasada</span>
                        </div>
                        {task.description && <p className="text-xs text-zinc-500">{task.description}</p>}
                        <p className="text-xs text-zinc-500 mt-0.5">Prazo era: {task.due_date ? formatDate(task.due_date) : "N/A"}</p>
                        <p className="text-[11px] text-zinc-400 dark:text-zinc-500 font-medium">
                          Casamento: {weddingMap[task.wedding] || "N/A"}
                        </p>
                      </div>
                    ))
                  )}
                </div>
              </SheetContent>
            </Sheet>
          )}
        </div>
      </div>

      {/* Card 4: Contratos Pendentes */}
      <div className={`bg-card p-5 rounded-xl shadow-soft relative overflow-hidden group border transition-all ${
        pendingContractsCount > 0
          ? "border-amber-200 dark:border-amber-900/30"
          : "border-zinc-200 dark:border-zinc-800"
      }`}>
        <div className={`absolute right-0 top-0 w-24 h-24 rounded-bl-full -mr-4 -mt-4 transition-transform group-hover:scale-110 duration-300 ${
          pendingContractsCount > 0
            ? "bg-amber-500/5 dark:bg-amber-500/10"
            : "bg-aura-500/5 dark:bg-aura-500/10"
        }`}></div>
        <div className="flex justify-between items-start mb-4 relative z-10">
          <div>
            <p className="text-sm font-medium text-zinc-500 dark:text-zinc-400">Contratos Pendentes</p>
            <h3 className={`font-mono text-2xl font-semibold mt-1 ${
              pendingContractsCount > 0 ? "text-amber-600 dark:text-amber-400" : "text-zinc-900 dark:text-white"
            }`}>
              {pendingContractsCount}
            </h3>
          </div>
          <div className={`w-10 h-10 rounded-lg flex items-center justify-center border transition-all ${
            pendingContractsCount > 0
              ? "bg-amber-50 dark:bg-amber-900/30 text-amber-600 dark:text-amber-400 border-amber-100 dark:border-amber-800/50"
              : "bg-zinc-50 dark:bg-zinc-800 text-zinc-400 border-zinc-100 dark:border-zinc-700"
          }`}>
            <FileText className="w-5 h-5" />
          </div>
        </div>
        <div className="flex items-center justify-between mt-4 relative z-10">
          <div className={`flex items-center text-xs font-medium w-max px-2 py-1 rounded border ${
            pendingContractsCount > 0
              ? "bg-amber-50 dark:bg-amber-900/20 text-amber-600 dark:text-amber-400 border-amber-100 dark:border-amber-800/30"
              : "bg-zinc-100 dark:bg-zinc-800 text-zinc-500 dark:text-zinc-400 border-transparent"
          }`}>
            <span>{pendingContractsCount > 0 ? "Aguardando assinatura/sinal" : "Nenhum pendente"}</span>
          </div>
          {pendingContractsCount > 0 && (
            <Sheet>
              <SheetTrigger asChild>
                <button className="text-xs font-medium text-amber-600 dark:text-amber-400 underline cursor-pointer hover:text-amber-800 dark:hover:text-amber-300 bg-transparent border-0 p-0">
                  Ver Contratos
                </button>
              </SheetTrigger>
              <SheetContent side="right" className="sm:max-w-md bg-white dark:bg-zinc-900 border-l border-zinc-200 dark:border-zinc-800 shadow-lg text-zinc-900 dark:text-zinc-100">
                <SheetHeader>
                  <SheetTitle className="flex items-center gap-2 text-amber-600 dark:text-amber-400 font-bold text-lg">
                    <FileText className="w-5 h-5" />
                    Contratos Pendentes
                  </SheetTitle>
                  <SheetDescription className="text-zinc-500 dark:text-zinc-400 text-sm">
                    Lista de contratos com fornecedores em rascunho ou pendentes de assinatura/sinal.
                  </SheetDescription>
                </SheetHeader>
                <div className="mt-6 space-y-3">
                  {isSharedLoading ? (
                    <div className="space-y-2">
                      <Skeleton className="h-14 w-full" />
                      <Skeleton className="h-14 w-full" />
                    </div>
                  ) : pendingContractsList.length === 0 ? (
                    <p className="text-sm text-zinc-500 text-center py-4">Nenhum contrato pendente.</p>
                  ) : (
                    pendingContractsList.map((contract) => (
                      <div key={contract.uuid} className="border border-amber-100 dark:border-amber-900/30 rounded-lg p-3 bg-amber-50/30 dark:bg-amber-900/10 flex justify-between items-center text-sm">
                        <div>
                          <p className="font-semibold text-zinc-900 dark:text-zinc-100">
                            {contract.supplier_name || "Fornecedor"}
                          </p>
                          {contract.description && <p className="text-xs text-zinc-500 mt-0.5">{contract.description}</p>}
                          <p className="text-[11px] text-zinc-400 dark:text-zinc-500 mt-0.5 font-medium">
                            Casamento: {weddingMap[contract.wedding] || "N/A"}
                          </p>
                        </div>
                        <span className="font-mono font-bold text-amber-600 dark:text-amber-400">
                          {formatCurrency(Number(contract.total_amount))}
                        </span>
                      </div>
                    ))
                  )}
                </div>
              </SheetContent>
            </Sheet>
          )}
        </div>
      </div>
    </div>
  );
}
