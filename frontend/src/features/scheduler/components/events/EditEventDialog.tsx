import { useCallback, useEffect } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import type { z } from "zod";
import { Lock } from "lucide-react";

import { useSchedulerEventsUpdate } from "@/api/generated/v1/endpoints/scheduler/scheduler";
import { SchedulerEventsUpdateBody } from "@/api/generated/v1/zod/scheduler/scheduler";
import { createMutationCallbacks } from "@/hooks/use-mutation-toast";
import type { EventOut } from "@/api/generated/v1/models/eventOut";

import { FormDialog } from "@/components/form-dialog";
import { FormInput, FormTextarea } from "@/components/form-fields";
import {
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { Checkbox } from "@/components/ui/checkbox";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { EVENT_TYPE_OPTIONS, RECURRENCE_OPTIONS } from "../../constants";
import { toDateTimeLocalValue, toISODateTime } from "../../utils";

interface EditEventDialogProps {
  event: EventOut;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess: () => void;
}

const NOOP = () => {};

const isPaymentEvent = (event: EventOut) => event.event_type === "pagamento";

export function EditEventDialog({
  event,
  open,
  onOpenChange,
  onSuccess,
}: EditEventDialogProps) {
  const { mutate, isPending } = useSchedulerEventsUpdate();
  const readOnly = isPaymentEvent(event);

  const form = useForm({
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

  if (readOnly) {
    return (
      <FormDialog
        open={open}
        onOpenChange={handleOpenChange}
        title="Detalhes do Evento"
        description="Evento de pagamento gerado automaticamente."
        form={form}
        onSubmit={NOOP}
        isPending={false}
        submitLabel="Fechar"
        submitDisabled={true}
        maxWidth="560px"
      >
        <Alert>
          <Lock className="h-4 w-4" />
          <AlertTitle>Evento somente leitura</AlertTitle>
          <AlertDescription>
            Este evento de pagamento foi gerado automaticamente a partir de
            uma parcela. Para modificá-lo, ajuste a parcela correspondente
            no módulo financeiro.
          </AlertDescription>
        </Alert>

        <div className="space-y-3 text-sm">
          <div>
            <span className="font-medium">Título: </span>
            {event.title}
          </div>
          <div>
            <span className="font-medium">Tipo: </span>Pagamento
          </div>
          <div>
            <span className="font-medium">Início: </span>
            {new Date(event.start_time).toLocaleString("pt-BR")}
          </div>
          {event.end_time && (
            <div>
              <span className="font-medium">Fim: </span>
              {new Date(event.end_time).toLocaleString("pt-BR")}
            </div>
          )}
          {event.location && (
            <div>
              <span className="font-medium">Local: </span>
              {event.location}
            </div>
          )}
          {event.description && (
            <div>
              <span className="font-medium">Descrição: </span>
              {event.description}
            </div>
          )}
        </div>
      </FormDialog>
    );
  }

  return (
    <FormDialog
      open={open}
      onOpenChange={handleOpenChange}
      title="Editar Evento"
      description="Atualize os dados do evento."
      form={form}
      onSubmit={form.handleSubmit(onSubmit)}
      isPending={isPending}
      submitLabel="Salvar Alterações"
      maxWidth="560px"
    >
      <FormInput
        control={form.control}
        name="title"
        label="Título"
        placeholder="Ex: Reunião com buffet"
      />

      <div className="grid grid-cols-2 gap-4">
        <FormField
          control={form.control}
          name="start_time"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Data/Hora Início</FormLabel>
              <FormControl>
                <Input
                  type="datetime-local"
                  value={
                    typeof field.value === "string"
                      ? toDateTimeLocalValue(field.value)
                      : ""
                  }
                  onChange={(e) => {
                    const v = e.target.value;
                    field.onChange(v ? toISODateTime(v) : "");
                  }}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="end_time"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Data/Hora Fim (opcional)</FormLabel>
              <FormControl>
                <Input
                  type="datetime-local"
                  value={
                    typeof field.value === "string"
                      ? toDateTimeLocalValue(field.value)
                      : ""
                  }
                  onChange={(e) => {
                    const v = e.target.value;
                    field.onChange(
                      v ? toISODateTime(v) : null,
                    );
                  }}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <FormField
          control={form.control}
          name="event_type"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Tipo</FormLabel>
              <Select onValueChange={field.onChange} value={field.value ?? undefined}>
                <FormControl>
                  <SelectTrigger>
                    <SelectValue placeholder="Selecione o tipo" />
                  </SelectTrigger>
                </FormControl>
                <SelectContent>
                  {EVENT_TYPE_OPTIONS.map((opt) => (
                    <SelectItem key={opt.value} value={opt.value}>
                      {opt.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="recurrence_rule"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Recorrência</FormLabel>
              <Select
                onValueChange={field.onChange}
                value={field.value ?? "none"}
              >
                <FormControl>
                  <SelectTrigger>
                    <SelectValue placeholder="Selecione" />
                  </SelectTrigger>
                </FormControl>
                <SelectContent>
                  {RECURRENCE_OPTIONS.map((opt) => (
                    <SelectItem key={opt.value} value={opt.value}>
                      {opt.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <FormMessage />
            </FormItem>
          )}
        />
      </div>

      <FormInput
        control={form.control}
        name="location"
        label="Local (opcional)"
        placeholder="Ex: Salão de Festas"
      />

      <FormTextarea
        control={form.control}
        name="description"
        label="Descrição (opcional)"
        placeholder="Detalhes adicionais do evento..."
      />

      <div className="flex items-center gap-6">
        <FormField
          control={form.control}
          name="reminder_enabled"
          render={({ field }) => (
            <FormItem className="flex flex-row items-start space-x-3 space-y-0">
              <FormControl>
                <Checkbox
                  checked={field.value ?? false}
                  onCheckedChange={field.onChange}
                />
              </FormControl>
              <FormLabel className="cursor-pointer">Ativar Lembrete</FormLabel>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="reminder_minutes_before"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Minutos antes</FormLabel>
              <FormControl>
                <Input
                  type="number"
                  min={0}
                  step={5}
                  className="w-24"
                  {...field}
                  value={field.value ?? 60}
                  onChange={(e) =>
                    field.onChange(
                      e.target.value === "" ? 60 : Number(e.target.value),
                    )
                  }
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
      </div>
    </FormDialog>
  );
}
