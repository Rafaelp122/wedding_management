import { useState, memo } from "react";
import { useForm, type Resolver } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { toast } from "sonner";
import type { z } from "zod";
import { AlertTriangle } from "lucide-react";

import {
  useLogisticsContractsCreateFull,
  useLogisticsContractsList,
  useLogisticsSuppliersList,
} from "@/api/generated/v1/endpoints/logistics/logistics";
import { useFinancesCategoriesList } from "@/api/generated/v1/endpoints/finances/finances";
import { LogisticsContractsCreateBody } from "@/api/generated/v1/zod/logistics/logistics";
import { SELECT_NONE_VALUE } from "@/lib/constants";
import { CONTRACT_STATUS_OPTIONS } from "@/features/logistics/constants";

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Input } from "@/components/ui/input";
import { Separator } from "@/components/ui/separator";
import { Loader2 } from "lucide-react";

import { FormInput, FormSelect, FormNumber, FormTextarea } from "@/components/form-fields";
import { ContractItemDrafts, type ItemDraft } from "./ContractItemDrafts";
import { ContractCreateExpenseFields } from "./ContractCreateExpenseFields";

type CreateContractFormData = z.infer<typeof LogisticsContractsCreateBody>;

interface ContractUploadDialogProps {
  weddingUuid: string;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess: () => void;
  prefilledParentUuid?: string | null;
}

export const ContractUploadDialog = memo(function ContractUploadDialog({
  weddingUuid,
  open,
  onOpenChange,
  onSuccess,
  prefilledParentUuid,
}: ContractUploadDialogProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const { mutateAsync: createFull, isPending: isCreating } =
    useLogisticsContractsCreateFull();

  const [itemDrafts, setItemDrafts] = useState<ItemDraft[]>([]);
  const [expenseChecked, setExpenseChecked] = useState(false);
  const [expenseCategory, setExpenseCategory] = useState("");
  const [expenseNumInstallments, setExpenseNumInstallments] = useState(1);
  const [expenseFirstDueDate, setExpenseFirstDueDate] = useState(
    () => new Date().toISOString().slice(0, 10),
  );

  const { data: suppliersResponse } = useLogisticsSuppliersList();
  const suppliers = suppliersResponse?.data?.items ?? [];

  const { data: contractsResponse } = useLogisticsContractsList({
    wedding_id: weddingUuid,
  });
  const existingContracts = contractsResponse?.data?.items ?? [];

  const { data: categoriesResponse } = useFinancesCategoriesList({
    wedding_id: weddingUuid,
  });
  const categories = categoriesResponse?.data?.items ?? [];

  const form = useForm<CreateContractFormData>({
    resolver: zodResolver(LogisticsContractsCreateBody) as Resolver<CreateContractFormData>,
    defaultValues: {
      wedding: weddingUuid,
      supplier: "",
      name: "",
      total_amount: undefined,
      status: "DRAFT",
      description: "",
      parent: prefilledParentUuid || null,
    },
  });

  const onSubmit = async (data: CreateContractFormData) => {
    try {
      const itemsData = JSON.stringify(
        itemDrafts.map((d) => ({
          name: d.name,
          quantity: d.quantity,
          acquisition_status: d.acquisition_status,
        })),
      );

      await createFull({
        data: {
          wedding: data.wedding,
          supplier: data.supplier,
          name: data.name,
          total_amount: data.total_amount,
          status: data.status,
          description: data.description,
          parent: data.parent ?? null,
          items_data: itemsData,
          create_expense: expenseChecked,
          expense_category: expenseChecked ? expenseCategory : null,
          expense_num_installments: expenseChecked
            ? expenseNumInstallments
            : null,
          expense_first_due_date: expenseChecked ? expenseFirstDueDate : null,
          pdf_file: selectedFile ?? null,
        },
      });

      toast.success("Contrato criado com sucesso!");
      form.reset();
      setItemDrafts([]);
      onSuccess();
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Erro desconhecido";
      toast.error(`Erro ao criar contrato: ${message}`);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[640px] max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Novo Contrato</DialogTitle>
          <DialogDescription>
            Vincule um fornecedor a este evento com um novo contrato.
          </DialogDescription>
        </DialogHeader>

        <Alert variant="default" className="border-amber-200 bg-amber-50">
          <AlertTriangle className="size-4 text-amber-600" />
          <AlertDescription className="text-amber-800 text-xs">
            Este sistema não substitui consultoria jurídica. Documentos são
            armazenados apenas para referência.
          </AlertDescription>
        </Alert>

        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <FormSelect
              control={form.control}
              name="supplier"
              label="Fornecedor"
              items={suppliers}
              getItemKey={(s) => s.uuid}
              getItemLabel={(s) => s.name}
              placeholder="Selecione um fornecedor"
            />

            <FormInput
              control={form.control}
              name="name"
              label="Nome do Contrato"
              placeholder="Ex: Buffet Completo"
            />

            <FormTextarea
              control={form.control}
              name="description"
              label="Descrição"
              placeholder="Descreva o objeto do contrato..."
            />

            <div className="grid grid-cols-2 gap-4">
              <FormNumber
                control={form.control}
                name="total_amount"
                label="Valor Total"
              />

              <FormSelect
                control={form.control}
                name="status"
                label="Status"
                items={CONTRACT_STATUS_OPTIONS.filter((o) => o.value !== "CANCELED")}
                getItemKey={(o) => o.value}
                getItemLabel={(o) => o.label}
              />
            </div>

            {(existingContracts.length > 0 || prefilledParentUuid) && (
              <FormField
                control={form.control}
                name="parent"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>
                      {prefilledParentUuid
                        ? "Aditivo do Contrato"
                        : "Contrato Original — Aditivo (Opcional)"}
                    </FormLabel>
                    {prefilledParentUuid ? (
                      <p className="text-sm text-muted-foreground">
                        Este contrato será criado como aditivo do contrato
                        selecionado.
                      </p>
                    ) : (
                      <Select
                        onValueChange={(v) =>
                          field.onChange(v === SELECT_NONE_VALUE ? null : v)
                        }
                        value={field.value ?? SELECT_NONE_VALUE}
                      >
                        <FormControl>
                          <SelectTrigger>
                            <SelectValue placeholder="Nenhum (contrato novo)" />
                          </SelectTrigger>
                        </FormControl>
                        <SelectContent>
                          <SelectItem value={SELECT_NONE_VALUE}>
                            Nenhum (contrato novo)
                          </SelectItem>
                          {existingContracts.map((c) => (
                            <SelectItem key={c.uuid} value={c.uuid}>
                              {c.name || c.description ||
                                c.uuid.substring(0, 8)}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    )}
                    <FormMessage />
                  </FormItem>
                )}
              />
            )}

            <Separator />

            <div className="space-y-1">
              <label className="text-sm font-medium">Documento (Opcional)</label>
              <Input
                type="file"
                accept=".pdf,.docx,.doc,.xlsx,.xls,.png,.jpg,.jpeg,.txt"
                className="text-sm"
                onChange={(e) => setSelectedFile(e.target.files?.[0] ?? null)}
              />
              <p className="text-[11px] text-muted-foreground">
                Formatos: PDF, Word, Excel, imagens
              </p>
            </div>

            <Separator />

            <ContractItemDrafts
              drafts={itemDrafts}
              onDraftsChange={setItemDrafts}
            />

            <Separator />

            <ContractCreateExpenseFields
              categories={categories}
              onExpenseChange={(v) => {
                setExpenseChecked(v.checked);
                setExpenseCategory(v.category);
                setExpenseNumInstallments(v.numInstallments);
                setExpenseFirstDueDate(v.firstDueDate);
              }}
            />

            <DialogFooter>
              <Button
                type="button"
                variant="outline"
                onClick={() => onOpenChange(false)}
                disabled={isCreating}
              >
                Cancelar
              </Button>
              <Button type="submit" disabled={isCreating}>
                {isCreating && <Loader2 className="mr-2 size-4 animate-spin" />}
                Criar Contrato
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
});
