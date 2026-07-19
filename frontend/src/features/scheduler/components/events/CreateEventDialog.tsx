import { useCreateEventForm } from "../../hooks/useCreateEventForm";
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

interface CreateEventDialogProps {
  weddingUuid: string;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess: () => void;
  /** Quando fornecido, pré-preenche o horário inicial (ex: clique no calendário) */
  defaultStartTime?: Date;
  /** Lista de casamentos para o seletor. Se vazia ou ausente, usa weddingUuid fixo. */
  weddingOptions?: { uuid: string; label: string }[];
}

export function CreateEventDialog({
  weddingUuid,
  open,
  onOpenChange,
  onSuccess,
  defaultStartTime,
  weddingOptions,
}: CreateEventDialogProps) {
  const { form, isPending, onSubmit, handleOpenChange } = useCreateEventForm({
    weddingUuid,
    defaultStartTime,
    onSuccess,
    onOpenChange,
  });

  return (
    <FormDialog
      open={open}
      onOpenChange={handleOpenChange}
      title="Novo Evento"
      description="Preencha os dados do novo evento no cronograma."
      form={form}
      onSubmit={form.handleSubmit(onSubmit)}
      isPending={isPending}
      submitLabel="Criar Evento"
      maxWidth="560px"
    >
      {/* Wedding selector — only shown when multiple weddings available */}
      {weddingOptions && weddingOptions.length > 1 && (
        <FormField
          control={form.control}
          name="wedding"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Casamento</FormLabel>
              <Select onValueChange={field.onChange} value={field.value}>
                <FormControl>
                  <SelectTrigger>
                    <SelectValue placeholder="Selecione o casamento" />
                  </SelectTrigger>
                </FormControl>
                <SelectContent>
                  {weddingOptions.map((w) => (
                    <SelectItem key={w.uuid} value={w.uuid}>
                      {w.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <FormMessage />
            </FormItem>
          )}
        />
      )}

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
              <FormLabel>Data/Hora Início *</FormLabel>
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
              <Select onValueChange={field.onChange} value={field.value}>
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
                  checked={field.value}
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
