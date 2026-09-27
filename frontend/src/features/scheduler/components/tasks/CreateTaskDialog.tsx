import { memo } from "react";
import { useQueryClient } from "@tanstack/react-query";

import {
  useSchedulerTasksCreate,
  getSchedulerTasksListQueryKey,
  getSchedulerTimelineCompressionGetQueryKey,
} from "@/api/generated/v1/endpoints/scheduler/scheduler";
import {
  getDashboardWeddingQueryKey,
  getDashboardSummaryQueryKey,
} from "@/api/generated/v1/endpoints/dashboard/dashboard";
import { createMutationCallbacks } from "@/hooks/use-mutation-toast";
import type { TaskIn } from "@/api/generated/v1/models/taskIn";

import {
  CreateTaskDialogView,
} from "./CreateTaskDialogView";
import type { CreateTaskFormData } from "../../utils/validation";

export interface CreateTaskDialogProps {
  weddingUuid: string;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess?: () => void;
}

export const CreateTaskDialog = memo(function CreateTaskDialog({
  weddingUuid,
  open,
  onOpenChange,
  onSuccess,
}: CreateTaskDialogProps) {
  const queryClient = useQueryClient();
  const { mutate, isPending } = useSchedulerTasksCreate();

  const handleSubmit = (data: CreateTaskFormData, onDone: () => void) => {
    const payload: TaskIn = {
      wedding: weddingUuid,
      title: data.title.trim(),
      description: data.description?.trim() || "",
      priority: data.priority || "MEDIUM",
      due_date: data.due_date ? data.due_date : null,
      is_completed: false,
    };

    mutate(
      { data: payload },
      createMutationCallbacks({
        successMsg: "Item de checklist criado com sucesso!",
        fallbackErrorMsg: "Erro ao criar item de checklist.",
        onSuccess: () => {
          queryClient.invalidateQueries({
            queryKey: getSchedulerTasksListQueryKey({ wedding_id: weddingUuid }),
          });
          queryClient.invalidateQueries({
            queryKey: getDashboardWeddingQueryKey(weddingUuid),
          });
          queryClient.invalidateQueries({
            queryKey: getDashboardSummaryQueryKey(),
          });
          queryClient.invalidateQueries({
            queryKey: getSchedulerTimelineCompressionGetQueryKey({
              wedding_id: weddingUuid,
            }),
          });
          onDone();
          onOpenChange(false);
          onSuccess?.();
        },
      }),
    );
  };

  return (
    <CreateTaskDialogView
      open={open}
      onOpenChange={onOpenChange}
      onSubmit={handleSubmit}
      isPending={isPending}
    />
  );
});
