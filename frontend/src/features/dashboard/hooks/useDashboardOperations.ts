import { useState, useMemo } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import type { WeddingOut } from "@/api/generated/v1/models/weddingOut";
import { formatWeddingName } from "../utils";
import {
  useSchedulerTasksList,
  useSchedulerTasksComplete,
  useSchedulerTasksReopen,
} from "@/api/generated/v1/endpoints/scheduler/scheduler";
import { useLogisticsContractsList } from "@/api/generated/v1/endpoints/logistics/logistics";

/**
 * Propriedades para o hook useDashboardOperations.
 */
interface UseDashboardOperationsProps {
  /** Lista de casamentos a serem gerenciados pelo dashboard. */
  weddings: WeddingOut[];
  /** Data de referência opcional para determinar a data atual (útil para testes). */
  referenceDate?: Date;
}

/**
 * Hook personalizado para gerenciar as operações do painel (dashboard).
 *
 * Este hook encapsula as chamadas de API, mutações e lógica de filtragem para
 * tarefas urgentes, casamentos futuros e contratos pendentes.
 *
 * @param props As propriedades de entrada do hook.
 * @param props.weddings A lista completa de casamentos.
 * @param props.referenceDate A data opcional que define o momento "atual".
 * @returns Um objeto com estados e callbacks necessários para renderizar o painel.
 */
export function useDashboardOperations({ weddings, referenceDate }: UseDashboardOperationsProps) {
  const [activeTab, setActiveTab] = useState<string>("tarefas");
  const queryClient = useQueryClient();

  // API query for Tasks (enabled only when Tasks tab is active)
  const { data: tasksRes, isLoading: isLoadingTasks } = useSchedulerTasksList(
    { limit: 100 },
    { query: { enabled: activeTab === "tarefas" } }
  );

  // API query for Contracts (enabled only when Contracts tab is active)
  const { data: contractsRes, isLoading: isLoadingContracts } = useLogisticsContractsList(
    { limit: 100 },
    { query: { enabled: activeTab === "contratos" } }
  );

  // Mutations for completing and reopening a task
  const invalidateTasksAndDashboard = () => {
    toast.success("Tarefa atualizada com sucesso!");
    queryClient.invalidateQueries({ queryKey: ["/api/v1/scheduler/tasks/"] });
    queryClient.invalidateQueries({ queryKey: ["/api/v1/dashboard/summary"] });
  };

  const onTaskMutationError = () => {
    toast.error("Erro ao atualizar a tarefa.");
  };

  const completeTaskMutation = useSchedulerTasksComplete({
    mutation: {
      onSuccess: invalidateTasksAndDashboard,
      onError: onTaskMutationError,
    },
  });

  const reopenTaskMutation = useSchedulerTasksReopen({
    mutation: {
      onSuccess: invalidateTasksAndDashboard,
      onError: onTaskMutationError,
    },
  });


  // 1. Process Grooms & Brides map for name resolution
  const weddingMap = useMemo(() => {
    return weddings.reduce((acc, w) => {
      acc[w.uuid] = formatWeddingName(w.bride_name, w.groom_name);
      return acc;
    }, {} as Record<string, string>);
  }, [weddings]);

  // 2. Upcoming Weddings
  const displayWeddings = useMemo(() => {
    return weddings.slice(0, 5);
  }, [weddings]);

  // 3. Urgent Tasks (Incomplete + sort by due date)
  const todayStr = useMemo(() => {
    const refDate = referenceDate || new Date();
    return refDate.toISOString().slice(0, 10);
  }, [referenceDate]);

  const urgentTasks = useMemo(() => {
    return (tasksRes?.data?.items ?? [])
      .filter((task) => !task.is_completed)
      .sort((a, b) => {
        if (!a.due_date) return 1;
        if (!b.due_date) return -1;
        return a.due_date.localeCompare(b.due_date);
      })
      .slice(0, 5);
  }, [tasksRes]);

  // 4. Pending Contracts (DRAFT or PENDING status)
  const pendingContracts = useMemo(() => {
    return (contractsRes?.data?.items ?? [])
      .filter((c) => c.status === "DRAFT" || c.status === "PENDING")
      .slice(0, 5);
  }, [contractsRes]);

  const handleTaskToggle = (taskUuid: string, isCurrentlyCompleted: boolean) => {
    if (isCurrentlyCompleted) {
      reopenTaskMutation.mutate({ uuid: taskUuid });
    } else {
      completeTaskMutation.mutate({ uuid: taskUuid });
    }
  };

  return {
    activeTab,
    setActiveTab,
    isLoadingTasks,
    isLoadingContracts,
    isUpdatingTask: completeTaskMutation.isPending || reopenTaskMutation.isPending,
    displayWeddings,
    urgentTasks,
    pendingContracts,
    weddingMap,
    handleTaskToggle,
    todayStr,
  };
}
