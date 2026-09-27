import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

import {
  useAddWeddingParticipant,
  getWeddingsReadQueryKey,
  getWeddingsListQueryKey,
} from "@/api/generated/v1/endpoints/weddings/weddings";
import {
  useListClients,
  useCreateClient,
  getListClientsQueryKey,
} from "@/api/generated/v1/endpoints/clients/clients";
import { WeddingParticipantRoleEnum } from "@/api/generated/v1/models/weddingParticipantRoleEnum";

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Checkbox } from "@/components/ui/checkbox";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Button } from "@/components/ui/button";

const ROLE_OPTIONS = [
  { value: WeddingParticipantRoleEnum.BRIDE, label: "Noiva" },
  { value: WeddingParticipantRoleEnum.GROOM, label: "Noivo" },
  { value: WeddingParticipantRoleEnum.FINANCIAL_PAYER, label: "Contratante Financeiro" },
  { value: WeddingParticipantRoleEnum.LEGAL_REPRESENTATIVE, label: "Representante Legal" },
  { value: WeddingParticipantRoleEnum.OTHER, label: "Outro Envolvido" },
];

const existingParticipantSchema = z.object({
  client_id: z.string().min(1, "Selecione um cliente cadastrado"),
  role: z.nativeEnum(WeddingParticipantRoleEnum, {
    message: "Selecione o papel do participante",
  }),
  is_primary_signatory: z.boolean(),
  notes: z.string(),
});

const newClientParticipantSchema = z.object({
  name: z.string().min(2, "Nome deve ter ao menos 2 caracteres"),
  cpf: z.string(),
  email: z.string().email("E-mail inválido").or(z.literal("")),
  phone: z.string(),
  role: z.nativeEnum(WeddingParticipantRoleEnum, {
    message: "Selecione o papel do participante",
  }),
  is_primary_signatory: z.boolean(),
  notes: z.string(),
});

type ExistingFormData = z.infer<typeof existingParticipantSchema>;
type NewClientFormData = z.infer<typeof newClientParticipantSchema>;

interface AddParticipantDialogProps {
  weddingUuid: string;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

/**
 * Smart Component para vincular participantes existentes ou cadastrar novos contatos (ADR-024).
 */
export function AddParticipantDialog({
  weddingUuid,
  open,
  onOpenChange,
}: AddParticipantDialogProps) {
  const [activeTab, setActiveTab] = useState<"existing" | "new">("existing");
  const queryClient = useQueryClient();

  const { data: clientsData, isLoading: isLoadingClients } = useListClients();
  const clients = clientsData?.data?.items ?? [];

  const addParticipantMutation = useAddWeddingParticipant({
    mutation: {
      onSuccess: () => {
        toast.success("Participante vinculado com sucesso!");
        queryClient.invalidateQueries({
          queryKey: getWeddingsReadQueryKey(weddingUuid),
        });
        queryClient.invalidateQueries({
          queryKey: getWeddingsListQueryKey(),
        });
        onOpenChange(false);
      },
      onError: (err: unknown) => {
        const errorMsg =
          (err as { response?: { data?: { detail?: string } } })?.response?.data
            ?.detail || "Erro ao vincular participante.";
        toast.error(errorMsg);
      },
    },
  });

  const createClientMutation = useCreateClient({
    mutation: {
      onSuccess: (newClient) => {
        queryClient.invalidateQueries({ queryKey: getListClientsQueryKey() });
        return newClient;
      },
    },
  });

  // Formulário para cliente existente
  const existingForm = useForm<ExistingFormData>({
    resolver: zodResolver(existingParticipantSchema),
    defaultValues: {
      client_id: "",
      role: WeddingParticipantRoleEnum.BRIDE,
      is_primary_signatory: false,
      notes: "",
    },
  });

  // Formulário para novo cliente
  const newClientForm = useForm<NewClientFormData>({
    resolver: zodResolver(newClientParticipantSchema),
    defaultValues: {
      name: "",
      cpf: "",
      email: "",
      phone: "",
      role: WeddingParticipantRoleEnum.BRIDE,
      is_primary_signatory: false,
      notes: "",
    },
  });

  const handleExistingSubmit = (data: ExistingFormData) => {
    addParticipantMutation.mutate({
      uuid: weddingUuid,
      data: {
        client_id: data.client_id,
        role: data.role,
        is_primary_signatory: data.is_primary_signatory,
        notes: data.notes || "",
      },
    });
  };

  const handleNewClientSubmit = async (data: NewClientFormData) => {
    try {
      const clientRes = await createClientMutation.mutateAsync({
        data: {
          name: data.name,
          cpf: data.cpf || undefined,
          email: data.email || undefined,
          phone: data.phone || undefined,
          notes: data.notes || undefined,
        },
      });

      addParticipantMutation.mutate({
        uuid: weddingUuid,
        data: {
          client_id: clientRes.data.uuid,
          role: data.role,
          is_primary_signatory: data.is_primary_signatory,
          notes: data.notes || "",
        },
      });
    } catch {
      toast.error("Não foi possível cadastrar o novo cliente.");
    }
  };

  const isPending =
    addParticipantMutation.isPending || createClientMutation.isPending;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[560px]">
        <DialogHeader>
          <DialogTitle>Vincular Participante ao Casamento</DialogTitle>
          <DialogDescription>
            Selecione um cliente já cadastrado na empresa ou cadastre uma nova pessoa.
          </DialogDescription>
        </DialogHeader>
      <Tabs
        value={activeTab}
        onValueChange={(val) => setActiveTab(val as "existing" | "new")}
        className="w-full"
      >
        <TabsList className="grid w-full grid-cols-2 mb-4">
          <TabsTrigger value="existing">Cliente Existente</TabsTrigger>
          <TabsTrigger value="new">Novo Contato / Cliente</TabsTrigger>
        </TabsList>

        <TabsContent value="existing">
          <Form {...existingForm}>
            <form
              onSubmit={existingForm.handleSubmit(handleExistingSubmit)}
              className="space-y-4"
              data-testid="form-existing-participant"
            >
              <FormField
                control={existingForm.control}
                name="client_id"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Cliente *</FormLabel>
                    <Select
                      onValueChange={field.onChange}
                      value={field.value}
                      disabled={isLoadingClients || isPending}
                    >
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Selecione o cliente" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        {clients.map((c) => (
                          <SelectItem key={c.uuid} value={c.uuid}>
                            {c.name} {c.cpf ? `(${c.cpf})` : ""}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={existingForm.control}
                name="role"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Papel no Evento *</FormLabel>
                    <Select
                      onValueChange={field.onChange}
                      value={field.value}
                      disabled={isPending}
                    >
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Selecione o papel" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        {ROLE_OPTIONS.map((opt) => (
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
                control={existingForm.control}
                name="is_primary_signatory"
                render={({ field }) => (
                  <FormItem className="flex flex-row items-center space-x-3 space-y-0 rounded-md border p-3">
                    <FormControl>
                      <Checkbox
                        checked={field.value}
                        onCheckedChange={field.onChange}
                        disabled={isPending}
                      />
                    </FormControl>
                    <div className="space-y-0.5">
                      <FormLabel className="text-sm font-medium cursor-pointer">
                        Signatário Principal do Contrato
                      </FormLabel>
                      <p className="text-xs text-muted-foreground">
                        Assina formalmente o contrato de prestação de serviços.
                      </p>
                    </div>
                  </FormItem>
                )}
              />

              <FormField
                control={existingForm.control}
                name="notes"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Observações</FormLabel>
                    <FormControl>
                      <Textarea
                        placeholder="Ex: Pai da noiva, responsável por 50% dos pagamentos."
                        className="resize-none h-20"
                        disabled={isPending}
                        {...field}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <div className="flex justify-end gap-2 pt-2">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => onOpenChange(false)}
                  disabled={isPending}
                >
                  Cancelar
                </Button>
                <Button type="submit" disabled={isPending}>
                  {isPending ? "Vinculando..." : "Vincular Participante"}
                </Button>
              </div>
            </form>
          </Form>
        </TabsContent>

        <TabsContent value="new">
          <Form {...newClientForm}>
            <form
              onSubmit={newClientForm.handleSubmit(handleNewClientSubmit)}
              className="space-y-4"
              data-testid="form-new-participant"
            >
              <FormField
                control={newClientForm.control}
                name="name"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Nome Completo *</FormLabel>
                    <FormControl>
                      <Input
                        placeholder="Ex: Roberto Albuquerque"
                        disabled={isPending}
                        {...field}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <FormField
                  control={newClientForm.control}
                  name="cpf"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>CPF</FormLabel>
                      <FormControl>
                        <Input
                          placeholder="000.000.000-00"
                          disabled={isPending}
                          {...field}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={newClientForm.control}
                  name="phone"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Telefone</FormLabel>
                      <FormControl>
                        <Input
                          placeholder="(11) 98888-0000"
                          disabled={isPending}
                          {...field}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>

              <FormField
                control={newClientForm.control}
                name="email"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>E-mail</FormLabel>
                    <FormControl>
                      <Input
                        type="email"
                        placeholder="roberto@exemplo.com"
                        disabled={isPending}
                        {...field}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={newClientForm.control}
                name="role"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Papel no Evento *</FormLabel>
                    <Select
                      onValueChange={field.onChange}
                      value={field.value}
                      disabled={isPending}
                    >
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Selecione o papel" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        {ROLE_OPTIONS.map((opt) => (
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
                control={newClientForm.control}
                name="is_primary_signatory"
                render={({ field }) => (
                  <FormItem className="flex flex-row items-center space-x-3 space-y-0 rounded-md border p-3">
                    <FormControl>
                      <Checkbox
                        checked={field.value}
                        onCheckedChange={field.onChange}
                        disabled={isPending}
                      />
                    </FormControl>
                    <div className="space-y-0.5">
                      <FormLabel className="text-sm font-medium cursor-pointer">
                        Signatário Principal do Contrato
                      </FormLabel>
                      <p className="text-xs text-muted-foreground">
                        Assina formalmente o contrato de prestação de serviços.
                      </p>
                    </div>
                  </FormItem>
                )}
              />

              <FormField
                control={newClientForm.control}
                name="notes"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Observações</FormLabel>
                    <FormControl>
                      <Textarea
                        placeholder="Anotações sobre este contato."
                        className="resize-none h-16"
                        disabled={isPending}
                        {...field}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <div className="flex justify-end gap-2 pt-2">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => onOpenChange(false)}
                  disabled={isPending}
                >
                  Cancelar
                </Button>
                <Button type="submit" disabled={isPending}>
                  {isPending ? "Cadastrando..." : "Cadastrar e Vincular"}
                </Button>
              </div>
            </form>
          </Form>
        </TabsContent>
      </Tabs>
      </DialogContent>
    </Dialog>
  );
}
