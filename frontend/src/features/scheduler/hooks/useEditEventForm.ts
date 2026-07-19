import { useCallback, useEffect } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import type { z } from "zod";
import { useSchedulerEventsUpdate } from "@/api/generated/v1/endpoints/scheduler/scheduler";
import { SchedulerEventsUpdateBody } from "@/api/generated/v1/zod/scheduler/scheduler";
import { createMutationCallbacks } from "@/hooks/use-mutation-toast";
import type { EventOut } from "@/api/generated/v1/models/eventOut";
import { toISODateTime } from "../utils";

interface UseEditEventFormProps {
  event: EventOut;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess: () => void;
}

const isPaymentEvent = (event: EventOut) => event.event_type === "pagamento";

/**
 * Hook para gerenciar o formulário de edição de eventos do cronograma.
 *
 * @param props Propriedades de configuração do formulário.
 * @returns Instância do formulário, estados, flag de somente leitura e callbacks.
 */
export function useEditEventForm({
  event,
  open,
  onOpenChange,
  onSuccess,
}: UseEditEventFormProps) {
  const { mutate, isPending } = useSchedulerEventsUpdate();
  const readOnly = isPaymentEvent(event);

  const form = useForm<z.input<typeof SchedulerEventsUpdateBody>, undefined, z.infer<typeof SchedulerEventsUpdateBody>>({
    resolver: zodResolver(SchedulerEventsUpdateBody),
    defaultValues: {
      title: event.title || "",
      event_type: event.event_type,
      start_time: event.start_time,
      end_time: event.end_time ?? null,
      location: event.location ?? "",
      description: event.description ?? "",
      recurrence_rule: event.recurrence_rule ?? "none",
      reminder_enabled: event.reminder_enabled,
      reminder_minutes_before: event.reminder_minutes_before,
    },
  });

  // Reset form when event changes
  useEffect(() => {
    if (open) {
      form.reset({
        title: event.title || "",
        event_type: event.event_type,
        start_time: event.start_time,
        end_time: event.end_time ?? null,
        location: event.location ?? "",
        description: event.description ?? "",
        recurrence_rule: event.recurrence_rule ?? "none",
        reminder_enabled: event.reminder_enabled,
        reminder_minutes_before: event.reminder_minutes_before,
      });
    }
  }, [event, open, form]);

  const handleOpenChange = useCallback(
    (newOpen: boolean) => {
      if (!newOpen) {
        form.reset();
      }
      onOpenChange(newOpen);
    },
    [form, onOpenChange],
  );

  const onSubmit = (data: z.infer<typeof SchedulerEventsUpdateBody>) => {
    if (readOnly) return;

    const payload = {
      ...data,
      start_time: data.start_time
        ? toISODateTime(data.start_time as string)
        : null,
      end_time: data.end_time
        ? toISODateTime(data.end_time as string)
        : null,
    };

    mutate(
      { uuid: event.uuid, data: payload },
      createMutationCallbacks({
        successMsg: "Evento atualizado com sucesso!",
        fallbackErrorMsg: "Erro ao atualizar evento.",
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
    readOnly,
    onSubmit,
    handleOpenChange,
  };
}
