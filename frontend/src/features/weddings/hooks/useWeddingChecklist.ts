import { useQueryClient } from "@tanstack/react-query";
import {
  useSchedulerTasksList,
  useSchedulerTasksUpdate,
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

  const { mutate: updateTask, isPending: isUpdating } = useSchedulerTasksUpdate(
    {
      mutation: {
        onSuccess: () => {
          queryClient.invalidateQueries({
            queryKey: getSchedulerTasksListQueryKey({ wedding_id: weddingUuid }),
          });
        },
      },
    },
  );

  const toggleTaskCompletion = (uuid: string, currentStatus: boolean) => {
    updateTask({
      taskUuid: uuid,
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
