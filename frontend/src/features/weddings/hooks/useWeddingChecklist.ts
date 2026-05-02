import { useQueryClient } from "@tanstack/react-query";
import {
  useSchedulerTasksList,
  useSchedulerTasksPartialUpdate,
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

  const { mutate: updateTask, isPending: isUpdating } =
    useSchedulerTasksPartialUpdate({
      mutation: {
        onSuccess: () => {
          queryClient.invalidateQueries({
            queryKey: getSchedulerTasksListQueryKey({ wedding_id: weddingUuid }),
          });
        },
      },
    });

  const toggleTaskCompletion = (uuid: string, currentStatus: boolean) => {
    updateTask({
      uuid,
      data: { is_completed: !currentStatus },
    });
  };

  return {
    tasks,
    isLoading,
    error,
    isUpdating,
    toggleTaskCompletion,
  };
}
