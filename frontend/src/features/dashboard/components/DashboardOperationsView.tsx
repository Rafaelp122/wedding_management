import {
  ArrowRight,
  Calendar,
  CheckSquare,
  FileText,
  Clock,
  ExternalLink,
} from "lucide-react";
import type { WeddingOut } from "@/api/generated/v1/models/weddingOut";
import type { TaskOut } from "@/api/generated/v1/models/taskOut";
import type { ContractOut } from "@/api/generated/v1/models/contractOut";
import { WeddingStatusEnum } from "@/api/generated/v1/models/weddingStatusEnum";
import { formatCurrencyBR, formatDateBR } from "@/lib/formatters";
import { formatWeddingName } from "../utils";
import { getWeddingStatusLabel } from "@/features/weddings/utils/wedding-status";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Checkbox } from "@/components/ui/checkbox";
import { Skeleton } from "@/components/ui/skeleton";

interface DashboardOperationsViewProps {
  activeTab: string;
  onTabChange: (tab: string) => void;
  isLoadingTasks: boolean;
  isLoadingContracts: boolean;
  isUpdatingTask: boolean;
  displayWeddings: WeddingOut[];
  urgentTasks: TaskOut[];
  pendingContracts: ContractOut[];
  weddingMap: Record<string, string>;
  handleTaskToggle: (taskUuid: string, isCurrentlyCompleted: boolean) => void;
  todayStr: string;
  onNavigateToWedding: (weddingUuid: string, tab?: string) => void;
}

export function DashboardOperationsView({
  activeTab,
  onTabChange,
  isLoadingTasks,
  isLoadingContracts,
  isUpdatingTask,
  displayWeddings,
  urgentTasks,
  pendingContracts,
  weddingMap,
  handleTaskToggle,
  todayStr,
  onNavigateToWedding,
}: DashboardOperationsViewProps) {
  return (
    <Card className="bg-card shadow-soft border-zinc-200 dark:border-zinc-800 overflow-hidden flex flex-col h-full">
      <Tabs value={activeTab} onValueChange={onTabChange} className="w-full flex flex-col h-full">
        <CardHeader className="p-6 border-b border-zinc-200 dark:border-zinc-800 flex flex-col sm:flex-row justify-between items-start sm:items-center bg-zinc-50/50 dark:bg-zinc-900/30 gap-4 shrink-0">
          <div>
            <CardTitle className="text-base font-semibold text-zinc-900 dark:text-white">
              {activeTab === "casamentos" && "Próximos Casamentos"}
              {activeTab === "tarefas" && "Checklist de Tarefas Urgentes"}
              {activeTab === "contratos" && "Contratos Pendentes com Fornecedores"}
            </CardTitle>
            <p className="text-xs text-zinc-500 dark:text-zinc-400 mt-1">
              {activeTab === "casamentos" && "Casamentos agendados ordenados cronologicamente"}
              {activeTab === "tarefas" && "Tarefas pendentes que precisam de atenção imediata"}
              {activeTab === "contratos" && "Contratos aguardando assinatura ou pagamento do sinal"}
            </p>
          </div>

          <TabsList className="bg-zinc-100 dark:bg-zinc-800 h-9 p-0.5 self-end sm:self-auto shrink-0">
            <TabsTrigger value="casamentos" className="h-8 text-xs gap-1.5">
              <Calendar className="w-3.5 h-3.5" />
              Casamentos
            </TabsTrigger>
            <TabsTrigger value="tarefas" className="h-8 text-xs gap-1.5">
              <CheckSquare className="w-3.5 h-3.5" />
              Tarefas
            </TabsTrigger>
            <TabsTrigger value="contratos" className="h-8 text-xs gap-1.5">
              <FileText className="w-3.5 h-3.5" />
              Contratos
            </TabsTrigger>
          </TabsList>
        </CardHeader>

        <CardContent className="p-0 flex-1 overflow-y-auto min-h-[300px]">
          {/* TAB: Upcoming Weddings */}
          <TabsContent value="casamentos" className="m-0 h-full w-full">
            <div className="overflow-x-auto w-full">
              <table className="w-full text-left border-collapse whitespace-nowrap">
                <thead>
                  <tr className="border-b border-zinc-200 dark:border-zinc-800 bg-white dark:bg-[#18181B]">
                    <th className="py-4 px-6 text-xs font-semibold text-zinc-500 dark:text-zinc-400 uppercase tracking-wider">Noivos</th>
                    <th className="py-4 px-6 text-xs font-semibold text-zinc-500 dark:text-zinc-400 uppercase tracking-wider">Data do Evento</th>
                    <th className="py-4 px-6 text-xs font-semibold text-zinc-500 dark:text-zinc-400 uppercase tracking-wider">Local</th>
                    <th className="py-4 px-6 text-xs font-semibold text-zinc-500 dark:text-zinc-400 uppercase tracking-wider text-center">Status</th>
                    <th className="py-4 px-6 text-xs font-semibold text-zinc-500 dark:text-zinc-400 uppercase tracking-wider text-right">Ação</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-zinc-100 dark:divide-zinc-800/60">
                  {displayWeddings.length === 0 ? (
                    <tr>
                      <td colSpan={5} className="py-8 text-center text-sm text-muted-foreground">
                        Nenhum casamento encontrado.
                      </td>
                    </tr>
                  ) : (
                    displayWeddings.map((wedding) => (
                      <tr key={wedding.uuid} className="table-row-hover">
                        <td className="py-4 px-6">
                          <p className="text-sm font-semibold text-zinc-900 dark:text-zinc-100">
                            {formatWeddingName(wedding.bride_name, wedding.groom_name)}
                          </p>
                        </td>
                        <td className="py-4 px-6">
                          <span className="text-sm text-zinc-600 dark:text-zinc-300">
                            {formatDateBR(wedding.date)}
                          </span>
                        </td>
                        <td className="py-4 px-6">
                          <span className="text-sm text-zinc-600 dark:text-zinc-300 truncate max-w-[200px] block">
                            {wedding.location || "Não definido"}
                          </span>
                        </td>
                        <td className="py-4 px-6 text-center">
                          <Badge
                            variant={
                              wedding.status === WeddingStatusEnum.COMPLETED ? "default" : "secondary"
                            }
                            className={`text-[10px] font-bold uppercase tracking-wider h-5 px-2.5 rounded-md ${
                              wedding.status === WeddingStatusEnum.COMPLETED
                                ? "bg-emerald-50 text-emerald-700 border border-emerald-200 dark:bg-emerald-500/10 dark:text-emerald-400 dark:border-emerald-500/20"
                                : "bg-violet-50 text-violet-700 border border-violet-200 dark:bg-violet-500/10 dark:text-violet-400 dark:border-violet-500/20"
                            }`}
                          >
                            {getWeddingStatusLabel(wedding.status)}
                          </Badge>
                        </td>
                        <td className="py-4 px-6 text-right">
                          <button
                            onClick={() => onNavigateToWedding(wedding.uuid)}
                            className="inline-flex items-center gap-1.5 bg-white dark:bg-zinc-800 border border-zinc-200 dark:border-zinc-700 hover:border-primary dark:hover:border-primary text-xs font-medium text-zinc-700 dark:text-zinc-300 hover:text-primary dark:hover:text-primary px-3 py-1.5 rounded-md btn-transition shadow-sm cursor-pointer"
                          >
                            Ver Detalhes
                            <ArrowRight className="size-3" />
                          </button>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </TabsContent>

          {/* TAB: Urgent Tasks */}
          <TabsContent value="tarefas" className="m-0 h-full w-full">
            {isLoadingTasks ? (
              <div className="p-6 space-y-4">
                {[...Array(3)].map((_, i) => (
                  <div key={i} className="flex gap-4 items-center">
                    <Skeleton className="w-4 h-4 rounded" />
                    <div className="space-y-2 flex-1">
                      <Skeleton className="h-4 w-48" />
                      <Skeleton className="h-3 w-32" />
                    </div>
                  </div>
                ))}
              </div>
            ) : urgentTasks.length === 0 ? (
              <div className="flex flex-col items-center justify-center text-center py-12 px-4">
                <CheckSquare className="w-8 h-8 text-zinc-300 dark:text-zinc-600 mb-3" />
                <p className="text-sm font-medium text-zinc-900 dark:text-white">Tudo em dia!</p>
                <p className="text-xs text-zinc-500 dark:text-zinc-400 mt-1">Parabéns, nenhuma tarefa pendente urgente.</p>
              </div>
            ) : (
              <div className="divide-y divide-zinc-100 dark:divide-zinc-800/60">
                {urgentTasks.map((task) => {
                  const isOverdue = task.due_date && task.due_date < todayStr;
                  return (
                    <div
                      key={task.uuid}
                      className="flex items-center justify-between p-4 hover:bg-zinc-50/50 dark:hover:bg-zinc-900/30 btn-transition"
                    >
                      <div className="flex items-start gap-3 flex-1 min-w-0 mr-4">
                        <Checkbox
                          id={`task-${task.uuid}`}
                          checked={task.is_completed}
                          onCheckedChange={() => handleTaskToggle(task.uuid, task.is_completed)}
                          className="mt-1 shrink-0"
                          disabled={isUpdatingTask}
                        />
                        <div className="min-w-0">
                          <label
                            htmlFor={`task-${task.uuid}`}
                            className={`text-sm font-medium text-zinc-900 dark:text-zinc-100 cursor-pointer block truncate ${
                              task.is_completed ? "line-through text-zinc-400 dark:text-zinc-600" : ""
                            }`}
                          >
                            {task.title}
                          </label>
                          <div className="flex items-center gap-2 mt-1 flex-wrap">
                            <span className="text-[11px] text-zinc-500 dark:text-zinc-400 font-medium">
                              Casamento: {weddingMap[task.wedding] || "Não definido"}
                            </span>
                            {task.due_date && (
                              <span className={`text-[11px] flex items-center gap-1 font-semibold ${
                                isOverdue ? "text-red-500" : "text-zinc-500 dark:text-zinc-400"
                              }`}>
                                <Clock className="w-3 h-3" />
                                Vence em: {formatDateBR(task.due_date)}
                                {isOverdue && <span className="bg-red-50 text-red-600 dark:bg-red-950/30 dark:text-red-400 px-1.5 py-0.2 rounded text-[9px] font-bold ml-1">Atrasada</span>}
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                      <button
                        onClick={() => onNavigateToWedding(task.wedding, "planning")}
                        className="text-xs text-primary hover:underline font-medium inline-flex items-center gap-1 shrink-0 cursor-pointer"
                      >
                        Ir para Cronograma
                        <ArrowRight className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  );
                })}
              </div>
            )}
          </TabsContent>

          {/* TAB: Pending Contracts */}
          <TabsContent value="contratos" className="m-0 h-full w-full">
            {isLoadingContracts ? (
              <div className="p-6 space-y-4">
                {[...Array(3)].map((_, i) => (
                  <Skeleton key={i} className="h-16 w-full rounded-lg" />
                ))}
              </div>
            ) : pendingContracts.length === 0 ? (
              <div className="flex flex-col items-center justify-center text-center py-12 px-4">
                <FileText className="w-8 h-8 text-zinc-300 dark:text-zinc-600 mb-3" />
                <p className="text-sm font-medium text-zinc-900 dark:text-white">Nenhum contrato pendente</p>
                <p className="text-xs text-zinc-500 dark:text-zinc-400 mt-1">Todos os contratos ativos estão assinados e finalizados.</p>
              </div>
            ) : (
              <div className="overflow-x-auto w-full">
                <table className="w-full text-left border-collapse whitespace-nowrap">
                  <thead>
                    <tr className="border-b border-zinc-200 dark:border-zinc-800 bg-white dark:bg-[#18181B]">
                      <th className="py-4 px-6 text-xs font-semibold text-zinc-500 dark:text-zinc-400 uppercase tracking-wider">Fornecedor</th>
                      <th className="py-4 px-6 text-xs font-semibold text-zinc-500 dark:text-zinc-400 uppercase tracking-wider">Casamento</th>
                      <th className="py-4 px-6 text-xs font-semibold text-zinc-500 dark:text-zinc-400 uppercase tracking-wider">Valor do Contrato</th>
                      <th className="py-4 px-6 text-xs font-semibold text-zinc-500 dark:text-zinc-400 uppercase tracking-wider text-center">Status</th>
                      <th className="py-4 px-6 text-xs font-semibold text-zinc-500 dark:text-zinc-400 uppercase tracking-wider text-right">Ação</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-zinc-100 dark:divide-zinc-800/60">
                    {pendingContracts.map((contract) => (
                      <tr key={contract.uuid} className="table-row-hover">
                        <td className="py-4 px-6">
                          <p className="text-sm font-semibold text-zinc-900 dark:text-zinc-100">
                            {contract.supplier_name}
                          </p>
                          {contract.description && (
                            <p className="text-xs text-zinc-500 dark:text-zinc-400 max-w-[200px] truncate">
                              {contract.description}
                            </p>
                          )}
                        </td>
                        <td className="py-4 px-6">
                          <span className="text-sm text-zinc-600 dark:text-zinc-300">
                            {weddingMap[contract.wedding] || "Não definido"}
                          </span>
                        </td>
                        <td className="py-4 px-6">
                          <span className="text-sm font-mono font-medium text-zinc-900 dark:text-zinc-100">
                            {formatCurrencyBR(Number(contract.total_amount))}
                          </span>
                        </td>
                        <td className="py-4 px-6 text-center">
                          <Badge
                            variant={contract.status === "DRAFT" ? "secondary" : "outline"}
                            className={`text-[10px] font-bold uppercase tracking-wider h-5 px-2.5 rounded-md ${
                              contract.status === "DRAFT"
                                ? "bg-zinc-100 text-zinc-700 dark:bg-zinc-800 dark:text-zinc-300"
                                : "bg-amber-50 text-amber-700 border-amber-200 dark:bg-amber-500/10 dark:text-amber-400 dark:border-amber-500/20"
                            }`}
                          >
                            {contract.status === "DRAFT" ? "Rascunho" : "Pendente"}
                          </Badge>
                        </td>
                        <td className="py-4 px-6 text-right">
                          <button
                            onClick={() => onNavigateToWedding(contract.wedding, "logistics")}
                            className="inline-flex items-center gap-1.5 bg-white dark:bg-zinc-800 border border-zinc-200 dark:border-zinc-700 hover:border-primary dark:hover:border-primary text-xs font-medium text-zinc-700 dark:text-zinc-300 hover:text-primary dark:hover:text-primary px-3 py-1.5 rounded-md btn-transition shadow-sm cursor-pointer"
                          >
                            <ExternalLink className="size-3" />
                            Ver Contrato
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </TabsContent>
        </CardContent>
      </Tabs>
    </Card>
  );
}
