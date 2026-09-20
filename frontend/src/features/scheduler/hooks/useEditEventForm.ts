import { useCallback, useEffect, useRef, useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import type { z } from "zod";
import { useSchedulerEventsUpdate } from "@/api/generated/v1/endpoints/scheduler/scheduler";
import { SchedulerEventsUpdateBody } from "@/api/generated/v1/zod/scheduler/scheduler";
import type { EventOut } from "@/api/generated/v1/models/eventOut";
import type { EventPatchIn } from "@/api/generated/v1/models/eventPatchIn";
import { getApiErrorInfo } from "@/api/error-utils";
import { toast } from "sonner";
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
  const [hasOverlapConflict, setHasOverlapConflict] = useState(false);
  const pendingPayloadRef = useRef<EventPatchIn | null>(null);

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
      setHasOverlapConflict(false);
      pendingPayloadRef.current = null;
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
        setHasOverlapConflict(false);
        pendingPayloadRef.current = null;
      }
      onOpenChange(newOpen);
    },
    [form, onOpenChange],
  );

  const executeUpdate = useCallback(
    (payload: EventPatchIn) => {
      mutate(
        { uuid: event.uuid, data: payload },
        {
          onSuccess: () => {
            toast.success("Evento atualizado com sucesso!");
            setHasOverlapConflict(false);
            pendingPayloadRef.current = null;
            form.reset();
            onSuccess();
          },
          onError: (error: unknown) => {
            const errorInfo = getApiErrorInfo(error, "Erro ao atualizar evento.");
            const isConflict =
              errorInfo.code === "event_schedule_conflict" ||
              (error as { response?: { data?: { code?: string } } })?.response?.data?.code === "event_schedule_conflict" ||
              errorInfo.message.toLowerCase().includes("conflito") ||
              errorInfo.message.toLowerCase().includes("compromisso agendado");

            if (isConflict) {
              pendingPayloadRef.current = payload;
              setHasOverlapConflict(true);
              return;
            }

            toast.error(errorInfo.message);
          },
        },
      );
    },
    [event.uuid, form, mutate, onSuccess],
  );

  const onSubmit = (data: z.infer<typeof SchedulerEventsUpdateBody>) => {
    if (readOnly) return;
    setHasOverlapConflict(false);

    const payload: EventPatchIn = {
      ...data,
      start_time: data.start_time
        ? toISODateTime(data.start_time as string)
        : null,
      end_time: data.end_time
        ? toISODateTime(data.end_time as string)
        : null,
    };

    executeUpdate(payload);
  };

  const confirmOverlap = useCallback(() => {
    if (!pendingPayloadRef.current) return;
    executeUpdate({
      ...pendingPayloadRef.current,
      force_overlap: true,
    });
  }, [executeUpdate]);

  const cancelOverlap = useCallback(() => {
    setHasOverlapConflict(false);
    pendingPayloadRef.current = null;
  }, []);

  return {
    form,
    isPending,
    readOnly,
    hasOverlapConflict,
    confirmOverlap,
    cancelOverlap,
    onSubmit,
    handleOpenChange,
  };
}
