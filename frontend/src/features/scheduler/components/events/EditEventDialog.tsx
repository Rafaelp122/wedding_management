import { useEditEventForm } from "../../hooks/useEditEventForm";
import { ReadOnlyEventDetails } from "./ReadOnlyEventDetails";
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
import { EVENT_TYPE_OPTIONS, RECURRENCE_OPTIONS } from "../../constants";
import { toDateTimeLocalValue, toISODateTime } from "../../utils";

interface EditEventDialogProps {
  event: EventOut;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess: () => void;
}

export function EditEventDialog({
  event,
  open,
  onOpenChange,
  onSuccess,
}: EditEventDialogProps) {
  const { form, isPending, readOnly, onSubmit, handleOpenChange } = useEditEventForm({
    event,
    open,
    onOpenChange,
    onSuccess,
  });

  if (readOnly) {
    return (
      <ReadOnlyEventDetails
        event={event}
        open={open}
        onOpenChange={handleOpenChange}
      />
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
