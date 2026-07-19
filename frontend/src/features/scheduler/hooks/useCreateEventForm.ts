import { useCallback } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useSchedulerEventsCreate } from "@/api/generated/v1/endpoints/scheduler/scheduler";
import { createMutationCallbacks } from "@/hooks/use-mutation-toast";
import { z } from "zod";
import { createEventSchema, type CreateEventFormData } from "../utils/validation";
import { toISODateTime } from "../utils";

interface UseCreateEventFormProps {
  weddingUuid: string;
  defaultStartTime?: Date;
  onSuccess: () => void;
  onOpenChange: (open: boolean) => void;
}

/**
 * Hook para gerenciar o formulário de criação de eventos do cronograma.
 *
 * @param props Propriedades de configuração do formulário.
 * @returns Instância do formulário, estados e callbacks de controle.
 */
export function useCreateEventForm({
  weddingUuid,
  defaultStartTime,
  onSuccess,
  onOpenChange,
}: UseCreateEventFormProps) {
  const { mutate, isPending } = useSchedulerEventsCreate();

  const defaultStartTimeIso = defaultStartTime?.toISOString() ?? "";

  const form = useForm<z.input<typeof createEventSchema>, undefined, CreateEventFormData>({
    resolver: zodResolver(createEventSchema),
    defaultValues: {
      wedding: weddingUuid,
      title: "",
      event_type: "reuniao",
      start_time: defaultStartTimeIso,
      end_time: null,
      location: "",
      description: "",
      recurrence_rule: "none",
      reminder_enabled: false,
      reminder_minutes_before: 60,
    },
  });

  const handleOpenChange = useCallback(
    (newOpen: boolean) => {
      if (!newOpen) {
        form.reset();
      }
      onOpenChange(newOpen);
    },
    [form, onOpenChange],
  );

  const onSubmit = (data: CreateEventFormData) => {
    const payload = {
      ...data,
      start_time: toISODateTime(data.start_time),
      end_time: data.end_time ? toISODateTime(data.end_time) : null,
    };

    mutate(
      { data: payload },
      createMutationCallbacks({
        successMsg: "Evento criado com sucesso!",
        fallbackErrorMsg: "Erro ao criar evento.",
        onSuccess: () => {
          form.reset();
          onSuccess();
        },
      }),
    );
  };

  return {
    form,
    isPending,
    onSubmit,
    handleOpenChange,
  };
}
