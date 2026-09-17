import { useQueryClient } from "@tanstack/react-query";
import {
  useSchedulerTasksList,
  useSchedulerTasksComplete,
  useSchedulerTasksReopen,
  getSchedulerTasksListQueryKey,
} from "@/api/generated/v1/endpoints/scheduler/scheduler";

export function useWeddingChecklist(weddingUuid: string) {
  const queryClient = useQueryClient();

  const {
    data: tasksResponse,
    isLoading,
    error,
  } = useSchedulerTasksList({ wedding_id: weddingUuid });

  const tasks = tasksResponse?.data?.items || [];

  const invalidateTasks = () => {
    queryClient.invalidateQueries({
      queryKey: getSchedulerTasksListQueryKey({ wedding_id: weddingUuid }),
    });
  };

  const { mutate: completeTask, isPending: isCompleting } =
    useSchedulerTasksComplete({
      mutation: {
        onSuccess: invalidateTasks,
      },
    });

  const { mutate: reopenTask, isPending: isReopening } =
    useSchedulerTasksReopen({
      mutation: {
        onSuccess: invalidateTasks,
      },
    });

  const toggleTaskCompletion = (uuid: string, currentStatus: boolean) => {
    if (currentStatus) {
      reopenTask({ uuid });
    } else {
      completeTask({ uuid });
    }
  };

  return {
    tasks,
    isLoading,
    error,
    isUpdating: isCompleting || isReopening,
    toggleTaskCompletion,
  };
}
