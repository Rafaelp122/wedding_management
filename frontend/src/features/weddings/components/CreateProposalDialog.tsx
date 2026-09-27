import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useQueryClient } from "@tanstack/react-query";

import {
  useCreateWeddingProposal,
  getWeddingsListQueryKey,
} from "@/api/generated/v1/endpoints/weddings/weddings";
import { getDashboardSummaryQueryKey } from "@/api/generated/v1/endpoints/dashboard/dashboard";
import { createMutationCallbacks } from "@/hooks/use-mutation-toast";

import { FormDialog } from "@/components/form-dialog";
import {
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { TEMPLATE_OPTIONS } from "../constants";

const createProposalSchema = z.object({
  groom_name: z.string().min(1, "Nome do noivo é obrigatório").max(100),
  bride_name: z.string().min(1, "Nome da noiva é obrigatório").max(100),
  date: z.string().min(1, "Data estimada é obrigatória"),
  location: z.string().max(255).optional(),
  expected_guests: z.number().int().min(1).optional().nullable(),
  template: z.string().nullable().optional(),
  client_name: z.string().max(255).optional(),
  client_cpf: z.string().max(14).optional(),
  client_email: z
    .string()
    .email("E-mail inválido")
    .or(z.literal(""))
    .optional(),
  client_phone: z.string().max(20).optional(),
  client_role: z.string().max(50).optional(),
});

type CreateProposalFormData = z.infer<typeof createProposalSchema>;

interface CreateProposalDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess?: () => void;
}

const CLIENT_ROLE_OPTIONS = [
  { value: "NOIVO", label: "Noivo" },
  { value: "NOIVA", label: "Noiva" },
  { value: "PAI", label: "Pai" },
  { value: "MAE", label: "Mãe" },
  { value: "OUTRO", label: "Outro" },
];

/**
 * Componente Smart para cadastro inicial de Proposta Comercial / Briefing.
 */
export function CreateProposalDialog({
  open,
  onOpenChange,
  onSuccess,
}: CreateProposalDialogProps) {
  const queryClient = useQueryClient();
  const { mutate, isPending } = useCreateWeddingProposal();

  const form = useForm<CreateProposalFormData>({
    resolver: zodResolver(createProposalSchema),
    defaultValues: {
      groom_name: "",
      bride_name: "",
      date: "",
      location: "",
      expected_guests: undefined,
      template: null,
      client_name: "",
      client_cpf: "",
      client_email: "",
      client_phone: "",
      client_role: "NOIVO",
    },
  });

  const onSubmit = (data: CreateProposalFormData) => {
    mutate(
      {
        data: {
          groom_name: data.groom_name,
          bride_name: data.bride_name,
          date: data.date,
          location: data.location || "",
          expected_guests: data.expected_guests ? Number(data.expected_guests) : null,
          template: data.template || null,
          client_name: data.client_name || "",
          client_cpf: data.client_cpf || "",
          client_email: data.client_email || "",
          client_phone: data.client_phone || "",
          client_role: data.client_role || "NOIVO",
        },
      },
      createMutationCallbacks({
        successMsg: "Proposta criada com sucesso!",
        fallbackErrorMsg: "Erro ao criar proposta.",
        onSuccess: () => {
          form.reset();
          queryClient.invalidateQueries({
            queryKey: getWeddingsListQueryKey(),
          });
          queryClient.invalidateQueries({
            queryKey: getDashboardSummaryQueryKey(),
          });
          onOpenChange(false);
          onSuccess?.();
        },
      }),
    );
  };

  return (
    <FormDialog
      open={open}
      onOpenChange={onOpenChange}
      title="Nova Proposta de Casamento"
      description="Cadastre o briefing inicial e dados do contratante para gerar a proposta comercial."
      form={form}
      onSubmit={form.handleSubmit(onSubmit)}
      isPending={isPending}
      submitLabel="Criar Proposta"
      maxWidth="600px"
    >
      <div className="space-y-4">
        {/* Seção 1: Dados do Evento */}
        <div>
          <h4 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-3">
            Dados do Casamento
          </h4>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <FormField
              control={form.control}
              name="groom_name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Nome do Noivo</FormLabel>
                  <FormControl>
                    <Input placeholder="Ex: Lucas Silva" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="bride_name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Nome da Noiva</FormLabel>
                  <FormControl>
                    <Input placeholder="Ex: Beatriz Lima" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="date"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Data Estimada</FormLabel>
                  <FormControl>
                    <Input type="date" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="location"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Local Previsto</FormLabel>
                  <FormControl>
                    <Input placeholder="Ex: Villa Borghese" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="expected_guests"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Convidados Estimados</FormLabel>
                  <FormControl>
                    <Input
                      type="number"
                      placeholder="Ex: 150"
                      value={typeof field.value === "number" ? field.value : ""}
                      onChange={(e) => {
                        const val = e.target.value;
                        field.onChange(val === "" ? null : Number(val));
                      }}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="template"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Modelo de Cronograma</FormLabel>
                  <Select
                    onValueChange={(val) =>
                      field.onChange(val === "none" ? null : val)
                    }
                    value={field.value ?? "none"}
                  >
                    <FormControl>
                      <SelectTrigger aria-label="Modelo de Cronograma">
                        <SelectValue placeholder="Selecione um modelo" />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      {TEMPLATE_OPTIONS.map((opt) => (
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
        </div>

        {/* Seção 2: Dados do Contratante Principal */}
        <div className="pt-2 border-t">
          <h4 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-3">
            Dados do Contratante Principal
          </h4>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <FormField
              control={form.control}
              name="client_name"
              render={({ field }) => (
                <FormItem className="sm:col-span-2">
                  <FormLabel>Nome do Contratante</FormLabel>
                  <FormControl>
                    <Input placeholder="Ex: Nome completo" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="client_cpf"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>CPF do Contratante</FormLabel>
                  <FormControl>
                    <Input placeholder="000.000.000-00" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="client_role"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Papel / Relação</FormLabel>
                  <Select
                    onValueChange={field.onChange}
                    value={field.value ?? "NOIVO"}
                  >
                    <FormControl>
                      <SelectTrigger aria-label="Papel / Relação">
                        <SelectValue placeholder="Selecione o papel" />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      {CLIENT_ROLE_OPTIONS.map((opt) => (
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
              name="client_email"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>E-mail do Contratante</FormLabel>
                  <FormControl>
                    <Input
                      type="email"
                      placeholder="cliente@email.com"
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="client_phone"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Telefone / WhatsApp</FormLabel>
                  <FormControl>
                    <Input placeholder="(11) 99999-9999" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
          </div>
        </div>
      </div>
    </FormDialog>
  );
}
