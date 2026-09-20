import { useState, useMemo } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import {
  useDashboardOperationsList,
  getDashboardOperationsListQueryKey,
  getDashboardSummaryQueryKey,
} from "@/api/generated/v1/endpoints/dashboard/dashboard";
import {
  useSchedulerTasksComplete,
  useSchedulerTasksReopen,
} from "@/api/generated/v1/endpoints/scheduler/scheduler";

/**
 * Propriedades para o hook useDashboardOperations.
 */
interface UseDashboardOperationsProps {
  /** Data de referência opcional para determinar a data atual (útil para testes). */
  referenceDate?: Date;
}

/**
 * Hook personalizado para gerenciar as operações do painel (dashboard).
 *
 * Utiliza o endpoint consolidado useDashboardOperationsList() para obter
 * os Top 5 casamentos futuros, tarefas urgentes e contratos pendentes,
 * eliminando busca de centenas de registros e manipulações pesadas no cliente.
 *
 * @param props As propriedades de entrada opcionais do hook.
 * @returns Um objeto com estados e callbacks necessários para renderizar o painel.
 */
export function useDashboardOperations(props?: UseDashboardOperationsProps) {
  const [activeTab, setActiveTab] = useState<string>("tarefas");
  const queryClient = useQueryClient();

  // Consolidated API query for Dashboard Operations
  const { data: operationsRes, isLoading: isLoadingOperations } =
    useDashboardOperationsList();

  // Mutations for completing and reopening a task
  const invalidateTasksAndDashboard = () => {
    toast.success("Tarefa atualizada com sucesso!");
    queryClient.invalidateQueries({ queryKey: getDashboardOperationsListQueryKey() });
    queryClient.invalidateQueries({ queryKey: getDashboardSummaryQueryKey() });
    queryClient.invalidateQueries({ queryKey: ["/api/v1/scheduler/tasks/"] });
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

  const displayWeddings = operationsRes?.data?.upcoming_weddings ?? [];
  const urgentTasks = operationsRes?.data?.urgent_tasks ?? [];
  const pendingContracts = operationsRes?.data?.pending_contracts ?? [];

  const todayStr = useMemo(() => {
    const refDate = props?.referenceDate || new Date();
    return refDate.toISOString().slice(0, 10);
  }, [props?.referenceDate]);

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
    isLoading: isLoadingOperations,
    isLoadingTasks: isLoadingOperations,
    isLoadingContracts: isLoadingOperations,
    isUpdatingTask: completeTaskMutation.isPending || reopenTaskMutation.isPending,
    displayWeddings,
    urgentTasks,
    pendingContracts,
    handleTaskToggle,
    todayStr,
  };
}
