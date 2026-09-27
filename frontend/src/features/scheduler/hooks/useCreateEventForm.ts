import { useCallback, useRef, useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useSchedulerEventsCreate } from "@/api/generated/v1/endpoints/scheduler/scheduler";
import type { EventIn } from "@/api/generated/v1/models/eventIn";
import { getApiErrorInfo } from "@/api/error-utils";
import { toast } from "sonner";
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
  const [hasOverlapConflict, setHasOverlapConflict] = useState(false);
  const pendingPayloadRef = useRef<EventIn | null>(null);

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
        setHasOverlapConflict(false);
        pendingPayloadRef.current = null;
      }
      onOpenChange(newOpen);
    },
    [form, onOpenChange],
  );

  const executeCreate = useCallback(
    (payload: EventIn) => {
      mutate(
        { data: payload },
        {
          onSuccess: () => {
            toast.success("Evento criado com sucesso!");
            setHasOverlapConflict(false);
            pendingPayloadRef.current = null;
            form.reset();
            onSuccess();
          },
          onError: (error: unknown) => {
            const errorInfo = getApiErrorInfo(error, "Erro ao criar evento.");
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
    [form, mutate, onSuccess],
  );

  const onSubmit = (data: CreateEventFormData) => {
    setHasOverlapConflict(false);
    const payload: EventIn = {
      ...data,
      start_time: toISODateTime(data.start_time),
      end_time: data.end_time ? toISODateTime(data.end_time) : null,
    };
    executeCreate(payload);
  };

  const confirmOverlap = useCallback(() => {
    if (!pendingPayloadRef.current) return;
    executeCreate({
      ...pendingPayloadRef.current,
      force_overlap: true,
    });
  }, [executeCreate]);

  const cancelOverlap = useCallback(() => {
    setHasOverlapConflict(false);
    pendingPayloadRef.current = null;
  }, []);

  return {
    form,
    isPending,
    hasOverlapConflict,
    confirmOverlap,
    cancelOverlap,
    onSubmit,
    handleOpenChange,
  };
}
