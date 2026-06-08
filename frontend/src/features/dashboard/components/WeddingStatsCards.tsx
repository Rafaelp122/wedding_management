import {
  CalendarHeart,
  PiggyBank,
  CheckSquare,
  FileText,
  AlertTriangle,
  Clock,
} from "lucide-react";
import type { WeddingDashboardOut } from "@/api/generated/v1/models/weddingDashboardOut";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet";

interface WeddingStatsCardsProps {
  data?: WeddingDashboardOut;
  isLoading?: boolean;
}

const formatCurrency = (value: number | string) =>
  new Intl.NumberFormat("pt-BR", {
    style: "currency",
    currency: "BRL",
  }).format(Number(value));

const formatDate = (dateStr: string | null | undefined) => {
  if (!dateStr) return "—";
  try {
    return new Date(dateStr).toLocaleDateString("pt-BR", { timeZone: "UTC" });
  } catch {
    return dateStr;
  }
};

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

  // Urgency thresholds for days
  const daysIsUrgent = daysUntil > 0 && daysUntil <= 30;
  const daysIsWarning = daysUntil > 30 && daysUntil <= 90;

  // Budget thresholds
  const budgetIsDanger = budgetPct >= 90;
  const budgetIsWarning = budgetPct >= 75 && budgetPct < 90;

  // Contracts pending
  const contractsPending = contractsTotal - contractsSigned;

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
      {/* Card 1: Dias até o Casamento */}
      <div
        className={`bg-card p-5 rounded-xl shadow-soft relative overflow-hidden group border transition-all ${
          daysIsUrgent
            ? "border-red-200 dark:border-red-900/30"
            : daysIsWarning
              ? "border-amber-200 dark:border-amber-900/30"
              : "border-zinc-200 dark:border-zinc-800"
        }`}
      >
        <div
          className={`absolute right-0 top-0 w-24 h-24 rounded-bl-full -mr-4 -mt-4 transition-transform group-hover:scale-110 duration-300 ${
            daysIsUrgent
              ? "bg-destructive/5 dark:bg-destructive/10"
              : daysIsWarning
                ? "bg-amber-500/5 dark:bg-amber-500/10"
                : "bg-aura-500/5 dark:bg-aura-500/10"
          }`}
        />
        <div className="flex justify-between items-start mb-4 relative z-10">
          <div>
            <p className="text-sm font-medium text-zinc-500 dark:text-zinc-400">
              Dias até o Casamento
            </p>
            <h3
              className={`font-mono text-2xl font-semibold mt-1 ${
                daysIsUrgent
                  ? "text-destructive"
                  : daysIsWarning
                    ? "text-amber-600 dark:text-amber-400"
                    : "text-zinc-900 dark:text-white"
              }`}
            >
              {daysUntil > 0 ? daysUntil : "Hoje!"}
            </h3>
          </div>
          <div
            className={`w-10 h-10 rounded-lg flex items-center justify-center border transition-all ${
              daysIsUrgent
                ? "bg-red-50 dark:bg-red-900/30 text-destructive border-red-100 dark:border-red-800/50"
                : daysIsWarning
                  ? "bg-amber-50 dark:bg-amber-900/30 text-amber-600 dark:text-amber-400 border-amber-100 dark:border-amber-800/50"
                  : "bg-aura-50 dark:bg-aura-900/30 text-aura-600 dark:text-aura-400 border-aura-100 dark:border-aura-800/50"
            }`}
          >
            <CalendarHeart className="w-5 h-5" />
          </div>
        </div>
        <div className="mt-4 relative z-10">
          <div
            className={`inline-flex items-center text-xs font-medium px-2 py-1 rounded border ${
              daysIsUrgent
                ? "bg-red-50 dark:bg-red-900/20 text-destructive border-red-100 dark:border-red-800/30"
                : daysIsWarning
                  ? "bg-amber-50 dark:bg-amber-900/20 text-amber-600 dark:text-amber-400 border-amber-100 dark:border-amber-800/30"
                  : "bg-zinc-100 dark:bg-zinc-800 text-zinc-500 dark:text-zinc-400 border-transparent"
            }`}
          >
            {daysIsUrgent
              ? "⚠️ Urgente — menos de 30 dias"
              : daysIsWarning
                ? "📅 Menos de 90 dias"
                : `${daysUntil} dias restantes`}
          </div>
        </div>
      </div>

      {/* Card 2: Orçamento Utilizado */}
      <div
        className={`bg-card p-5 rounded-xl shadow-soft relative overflow-hidden group border transition-all ${
          budgetIsDanger
            ? "border-red-200 dark:border-red-900/30"
            : budgetIsWarning
              ? "border-amber-200 dark:border-amber-900/30"
              : "border-zinc-200 dark:border-zinc-800"
        }`}
      >
        <div
          className={`absolute right-0 top-0 w-24 h-24 rounded-bl-full -mr-4 -mt-4 transition-transform group-hover:scale-110 duration-300 ${
            budgetIsDanger
              ? "bg-destructive/5 dark:bg-destructive/10"
              : budgetIsWarning
                ? "bg-amber-500/5 dark:bg-amber-500/10"
                : "bg-aura-500/5 dark:bg-aura-500/10"
          }`}
        />
        <div className="flex justify-between items-start mb-3 relative z-10">
          <div>
            <p className="text-sm font-medium text-zinc-500 dark:text-zinc-400">
              Orçamento Utilizado
            </p>
            <h3
              className={`font-mono text-2xl font-semibold mt-1 ${
                budgetIsDanger
                  ? "text-destructive"
                  : budgetIsWarning
                    ? "text-amber-600 dark:text-amber-400"
                    : "text-zinc-900 dark:text-white"
              }`}
            >
              {budgetPct.toFixed(1)}%
            </h3>
          </div>
          <div
            className={`w-10 h-10 rounded-lg flex items-center justify-center border transition-all ${
              budgetIsDanger
                ? "bg-red-50 dark:bg-red-900/30 text-destructive border-red-100 dark:border-red-800/50"
                : budgetIsWarning
                  ? "bg-amber-50 dark:bg-amber-900/30 text-amber-600 dark:text-amber-400 border-amber-100 dark:border-amber-800/50"
                  : "bg-aura-50 dark:bg-aura-900/30 text-aura-600 dark:text-aura-400 border-aura-100 dark:border-aura-800/50"
            }`}
          >
            <PiggyBank className="w-5 h-5" />
          </div>
        </div>
        {/* Progress bar */}
        <div className="mt-1 mb-3 relative z-10">
          <div className="w-full bg-zinc-100 dark:bg-zinc-800 rounded-full h-1.5">
            <div
              className={`h-1.5 rounded-full transition-all duration-500 ${
                budgetIsDanger
                  ? "bg-destructive"
                  : budgetIsWarning
                    ? "bg-amber-500"
                    : "bg-aura-500"
              }`}
              style={{ width: `${Math.min(budgetPct, 100)}%` }}
            />
          </div>
        </div>
        <div className="flex items-center justify-between relative z-10">
          <div
            className={`inline-flex items-center text-xs font-medium px-2 py-1 rounded border ${
              budgetIsDanger
                ? "bg-red-50 dark:bg-red-900/20 text-destructive border-red-100 dark:border-red-800/30"
                : budgetIsWarning
                  ? "bg-amber-50 dark:bg-amber-900/20 text-amber-600 dark:text-amber-400 border-amber-100 dark:border-amber-800/30"
                  : "bg-zinc-100 dark:bg-zinc-800 text-zinc-500 dark:text-zinc-400 border-transparent"
            }`}
          >
            {budgetIsDanger
              ? "Limite crítico"
              : budgetIsWarning
                ? "Atenção ao budget"
                : "Dentro do orçamento"}
          </div>
          {upcomingInstallments.length > 0 && (
            <Sheet>
              <SheetTrigger asChild>
                <button className="text-xs font-medium text-aura-600 dark:text-aura-400 underline cursor-pointer hover:text-aura-800 dark:hover:text-aura-300 bg-transparent border-0 p-0">
                  Ver Parcelas
                </button>
              </SheetTrigger>
              <SheetContent
                side="right"
                className="sm:max-w-md bg-white dark:bg-zinc-900 border-l border-zinc-200 dark:border-zinc-800 shadow-lg text-zinc-900 dark:text-zinc-100"
              >
                <SheetHeader>
                  <SheetTitle className="flex items-center gap-2 text-aura-600 dark:text-aura-400 font-bold text-lg">
                    <Clock className="w-5 h-5" />
                    Próximas Parcelas
                  </SheetTitle>
                  <SheetDescription className="text-zinc-500 dark:text-zinc-400 text-sm">
                    Parcelas pendentes e vencidas nos próximos 30 dias.
                  </SheetDescription>
                </SheetHeader>
                <div className="mt-6 space-y-3">
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
                            {formatDate(String(inst.due_date))}
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
                          {formatCurrency(inst.amount)}
                        </span>
                      </div>
                    );
                  })}
                </div>
              </SheetContent>
            </Sheet>
          )}
        </div>
      </div>

      {/* Card 3: Tarefas */}
      <div
        className={`bg-card p-5 rounded-xl shadow-soft relative overflow-hidden group border transition-all ${
          tasksTotal > 0 && tasksCompleted < tasksTotal
            ? "border-amber-200 dark:border-amber-900/30"
            : "border-zinc-200 dark:border-zinc-800"
        }`}
      >
        <div
          className={`absolute right-0 top-0 w-24 h-24 rounded-bl-full -mr-4 -mt-4 transition-transform group-hover:scale-110 duration-300 ${
            tasksTotal > 0 && tasksCompleted < tasksTotal
              ? "bg-amber-500/5 dark:bg-amber-500/10"
              : "bg-aura-500/5 dark:bg-aura-500/10"
          }`}
        />
        <div className="flex justify-between items-start mb-3 relative z-10">
          <div>
            <p className="text-sm font-medium text-zinc-500 dark:text-zinc-400">
              Tarefas Concluídas
            </p>
            <h3 className="font-mono text-2xl font-semibold mt-1 text-zinc-900 dark:text-white">
              {tasksCompleted}
              <span className="text-base text-zinc-400 dark:text-zinc-500 font-normal">
                {" "}
                / {tasksTotal}
              </span>
            </h3>
          </div>
          <div
            className={`w-10 h-10 rounded-lg flex items-center justify-center border transition-all ${
              tasksTotal > 0 && tasksCompleted < tasksTotal
                ? "bg-amber-50 dark:bg-amber-900/30 text-amber-600 dark:text-amber-400 border-amber-100 dark:border-amber-800/50"
                : "bg-aura-50 dark:bg-aura-900/30 text-aura-600 dark:text-aura-400 border-aura-100 dark:border-aura-800/50"
            }`}
          >
            <CheckSquare className="w-5 h-5" />
          </div>
        </div>
        {/* Progress bar */}
        <div className="mt-1 mb-3 relative z-10">
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
        </div>
        <div className="flex items-center justify-between relative z-10">
          <div
            className={`inline-flex items-center text-xs font-medium px-2 py-1 rounded border ${
              tasksTotal > 0 && tasksCompleted === tasksTotal
                ? "bg-success/10 text-success border-transparent"
                : "bg-amber-50 dark:bg-amber-900/20 text-amber-600 dark:text-amber-400 border-amber-100 dark:border-amber-800/30"
            }`}
          >
            {tasksTotal > 0 && tasksCompleted === tasksTotal
              ? "✓ Todas concluídas"
              : `${tasksTotal - tasksCompleted} pendente${tasksTotal - tasksCompleted !== 1 ? "s" : ""}`}
          </div>
          {urgentTasks.length > 0 && (
            <Sheet>
              <SheetTrigger asChild>
                <button className="text-xs font-medium text-amber-600 dark:text-amber-400 underline cursor-pointer hover:text-amber-800 dark:hover:text-amber-300 bg-transparent border-0 p-0">
                  Ver Urgentes
                </button>
              </SheetTrigger>
              <SheetContent
                side="right"
                className="sm:max-w-md bg-white dark:bg-zinc-900 border-l border-zinc-200 dark:border-zinc-800 shadow-lg text-zinc-900 dark:text-zinc-100"
              >
                <SheetHeader>
                  <SheetTitle className="flex items-center gap-2 text-amber-600 dark:text-amber-400 font-bold text-lg">
                    <AlertTriangle className="w-5 h-5" />
                    Tarefas Urgentes
                  </SheetTitle>
                  <SheetDescription className="text-zinc-500 dark:text-zinc-400 text-sm">
                    Tarefas pendentes com prazo vencido ou sem data.
                  </SheetDescription>
                </SheetHeader>
                <div className="mt-6 space-y-3">
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
                          ? `Prazo: ${formatDate(String(task.due_date))}`
                          : "Sem data definida"}
                      </p>
                    </div>
                  ))}
                </div>
              </SheetContent>
            </Sheet>
          )}
        </div>
      </div>

      {/* Card 4: Contratos */}
      <div
        className={`bg-card p-5 rounded-xl shadow-soft relative overflow-hidden group border transition-all ${
          contractsPending > 0
            ? "border-amber-200 dark:border-amber-900/30"
            : "border-zinc-200 dark:border-zinc-800"
        }`}
      >
        <div
          className={`absolute right-0 top-0 w-24 h-24 rounded-bl-full -mr-4 -mt-4 transition-transform group-hover:scale-110 duration-300 ${
            contractsPending > 0
              ? "bg-amber-500/5 dark:bg-amber-500/10"
              : "bg-aura-500/5 dark:bg-aura-500/10"
          }`}
        />
        <div className="flex justify-between items-start mb-3 relative z-10">
          <div>
            <p className="text-sm font-medium text-zinc-500 dark:text-zinc-400">
              Contratos Assinados
            </p>
            <h3 className="font-mono text-2xl font-semibold mt-1 text-zinc-900 dark:text-white">
              {contractsSigned}
              <span className="text-base text-zinc-400 dark:text-zinc-500 font-normal">
                {" "}
                / {contractsTotal}
              </span>
            </h3>
          </div>
          <div
            className={`w-10 h-10 rounded-lg flex items-center justify-center border transition-all ${
              contractsPending > 0
                ? "bg-amber-50 dark:bg-amber-900/30 text-amber-600 dark:text-amber-400 border-amber-100 dark:border-amber-800/50"
                : "bg-aura-50 dark:bg-aura-900/30 text-aura-600 dark:text-aura-400 border-aura-100 dark:border-aura-800/50"
            }`}
          >
            <FileText className="w-5 h-5" />
          </div>
        </div>
        {/* Progress bar */}
        <div className="mt-1 mb-3 relative z-10">
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
        </div>
        <div className="mt-4 relative z-10">
          <div
            className={`inline-flex items-center text-xs font-medium px-2 py-1 rounded border ${
              contractsPending > 0
                ? "bg-amber-50 dark:bg-amber-900/20 text-amber-600 dark:text-amber-400 border-amber-100 dark:border-amber-800/30"
                : "bg-zinc-100 dark:bg-zinc-800 text-zinc-500 dark:text-zinc-400 border-transparent"
            }`}
          >
            {contractsPending > 0
              ? `${contractsPending} pendente${contractsPending !== 1 ? "s" : ""} de assinatura`
              : contractsTotal === 0
                ? "Nenhum contrato"
                : "✓ Todos assinados"}
          </div>
        </div>
      </div>
    </div>
  );
}
