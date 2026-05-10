import { useState, memo } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { toast } from "sonner";
import type { z } from "zod";
import { AlertTriangle, Plus, Check, X } from "lucide-react";

import {
  useLogisticsContractsCreate,
  useLogisticsContractsList,
  useLogisticsSuppliersList,
  useLogisticsItemsCreate,
} from "@/api/generated/v1/endpoints/logistics/logistics";
import {
  useFinancesExpensesCreate,
  useFinancesCategoriesList,
} from "@/api/generated/v1/endpoints/finances/finances";
import { AXIOS_INSTANCE } from "@/api/axios-client";
import { LogisticsContractsCreateBody } from "@/api/generated/v1/zod/logistics/logistics";
import { getApiErrorInfo } from "@/api/error-utils";

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
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Checkbox } from "@/components/ui/checkbox";
import { Separator } from "@/components/ui/separator";
import { Loader2 } from "lucide-react";

type CreateContractFormData = z.infer<typeof LogisticsContractsCreateBody>;

interface ItemDraft {
  key: string;
  name: string;
  quantity: number;
  acquisition_status: string;
}

const ITEM_STATUS_LABELS: Record<string, string> = {
  PENDING: "Pendente",
  IN_PROGRESS: "Em Andamento",
  DONE: "Concluído",
};

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
  const { mutateAsync: createContract, isPending: isCreating } =
    useLogisticsContractsCreate();
  const { mutateAsync: createItem } = useLogisticsItemsCreate();
  const { mutateAsync: createExpense } = useFinancesExpensesCreate();

  const [createExpenseChecked, setCreateExpenseChecked] = useState(false);
  const [expenseCategory, setExpenseCategory] = useState("");
  const [numInstallments, setNumInstallments] = useState(1);
  const [firstDueDate, setFirstDueDate] = useState(
    () => new Date().toISOString().slice(0, 10),
  );

  const [itemDrafts, setItemDrafts] = useState<ItemDraft[]>([]);
  const [showItemForm, setShowItemForm] = useState(false);
  const [itemName, setItemName] = useState("");
  const [itemQty, setItemQty] = useState(1);
  const [itemStatus, setItemStatus] = useState("PENDING");

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
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    resolver: zodResolver(LogisticsContractsCreateBody) as any,
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

  const addDraft = () => {
    if (!itemName.trim()) return;
    setItemDrafts([
      ...itemDrafts,
      { key: crypto.randomUUID(), name: itemName.trim(), quantity: itemQty, acquisition_status: itemStatus },
    ]);
    setItemName("");
    setItemQty(1);
    setItemStatus("PENDING");
    setShowItemForm(false);
  };

  const removeDraft = (key: string) => {
    setItemDrafts(itemDrafts.filter((d) => d.key !== key));
  };

  const onSubmit = async (data: CreateContractFormData) => {
    try {
      // 1. Cria contrato
      const result = await createContract({ data });
      const contractUuid = (result as { data: { uuid: string } }).data.uuid;

      // 2. Upload do arquivo (se houver)
      const file = selectedFile;
      if (file) {
        const formData = new FormData();
        formData.append("pdf_file", file);
        try {
          await AXIOS_INSTANCE.post(
            `/api/v1/logistics/contracts/${contractUuid}/upload/`,
            formData,
          );
        } catch {
          toast.warning("Contrato criado, mas o upload do documento falhou.");
        }
      }

      // 3. Cria itens (se houver)
      for (const draft of itemDrafts) {
        try {
          await createItem({
            data: {
              wedding: weddingUuid,
              contract: contractUuid,
              name: draft.name,
              quantity: draft.quantity,
              acquisition_status: draft.acquisition_status,
            },
          });
        } catch {
          // item creation failed — non-blocking
        }
      }

      // 4. Cria despesa (se checkbox marcado)
      if (createExpenseChecked && data.total_amount) {
        try {
          await createExpense({
            data: {
              category: expenseCategory,
              contract: contractUuid,
              name: data.name || data.description || "Despesa",
              description: data.description || null,
              estimated_amount: Number(data.total_amount),
              actual_amount: Number(data.total_amount),
              num_installments: numInstallments,
              first_due_date: firstDueDate || null,
            },
          });
        } catch {
          toast.warning("Contrato criado, mas a criação da despesa falhou.");
        }
      }

      toast.success("Contrato criado com sucesso!");
      form.reset();
      setCreateExpenseChecked(false);
      setItemDrafts([]);
      onSuccess();
    } catch (error) {
      const { message } = getApiErrorInfo(error, "Erro ao criar contrato.");
      toast.error(message);
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
            <FormField
              control={form.control}
              name="supplier"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Fornecedor</FormLabel>
                  <Select onValueChange={field.onChange} value={field.value}>
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue placeholder="Selecione um fornecedor" />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      {suppliers.map((s) => (
                        <SelectItem key={s.uuid} value={s.uuid}>
                          {s.name}
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
              name="name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Nome do Contrato</FormLabel>
                  <FormControl>
                    <Input {...field} placeholder="Ex: Buffet Completo" />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="description"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Descrição</FormLabel>
                  <FormControl>
                    <Textarea
                      {...field}
                      placeholder="Descreva o objeto do contrato..."
                      rows={2}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <div className="grid grid-cols-2 gap-4">
              <FormField
                control={form.control}
                name="total_amount"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Valor Total</FormLabel>
                    <FormControl>
                      <Input
                        type="number"
                        step="0.01"
                        min="0"
                        placeholder="0.00"
                        value={field.value ?? ""}
                        onBlur={field.onBlur}
                        name={field.name}
                        ref={field.ref}
                        onChange={(e) =>
                          field.onChange(
                            e.target.value === ""
                              ? undefined
                              : Number(e.target.value),
                          )
                        }
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="status"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Status</FormLabel>
                    <Select onValueChange={field.onChange} value={field.value}>
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        <SelectItem value="DRAFT">Rascunho</SelectItem>
                        <SelectItem value="PENDING">Pendente</SelectItem>
                        <SelectItem value="SIGNED">Assinado</SelectItem>
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
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
                          field.onChange(v === "__none__" ? null : v)
                        }
                        value={field.value ?? "__none__"}
                      >
                        <FormControl>
                          <SelectTrigger>
                            <SelectValue placeholder="Nenhum (contrato novo)" />
                          </SelectTrigger>
                        </FormControl>
                        <SelectContent>
                          <SelectItem value="__none__">
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

            {/* Documento */}
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

            {/* Itens */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="text-sm font-medium">Itens (Opcional)</label>
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  className="h-7 text-xs"
                  onClick={() => setShowItemForm(!showItemForm)}
                >
                  <Plus className="size-3 mr-1" />
                  Adicionar
                </Button>
              </div>

              {showItemForm && (
                <div className="flex gap-2 mb-3">
                  <Input
                    placeholder="Nome do item"
                    value={itemName}
                    onChange={(e) => setItemName(e.target.value)}
                    className="h-8 text-sm flex-1"
                    onKeyDown={(e) => { if (e.key === "Enter") { e.preventDefault(); addDraft(); } }}
                  />
                  <Input
                    type="number"
                    min={1}
                    value={itemQty}
                    onChange={(e) => setItemQty(Math.max(1, Number(e.target.value) || 1))}
                    className="h-8 text-sm w-16"
                  />
                  <Select value={itemStatus} onValueChange={setItemStatus}>
                    <SelectTrigger className="h-8 text-sm w-28">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="PENDING">Pendente</SelectItem>
                      <SelectItem value="IN_PROGRESS">Em Andamento</SelectItem>
                      <SelectItem value="DONE">Concluído</SelectItem>
                    </SelectContent>
                  </Select>
                  <Button
                    type="button"
                    size="sm"
                    className="h-8 text-xs shrink-0"
                    onClick={addDraft}
                  >
                    <Check className="size-3" />
                  </Button>
                </div>
              )}

              {itemDrafts.map((d) => (
                <div
                  key={d.key}
                  className="flex items-center gap-2 text-sm py-1.5 border-b last:border-0"
                >
                  <span className="flex-1 truncate">{d.name}</span>
                  <span className="w-10 text-center text-muted-foreground text-xs">
                    {d.quantity}
                  </span>
                  <Badge className="text-[10px] h-5" variant="outline">
                    {ITEM_STATUS_LABELS[d.acquisition_status] || d.acquisition_status}
                  </Badge>
                  <Button
                    type="button"
                    variant="ghost"
                    size="icon"
                    className="size-6"
                    onClick={() => removeDraft(d.key)}
                  >
                    <X className="size-3" />
                  </Button>
                </div>
              ))}

              {itemDrafts.length === 0 && !showItemForm && (
                <p className="text-xs text-muted-foreground">
                  Nenhum item adicionado.
                </p>
              )}
            </div>

            <Separator />

            {/* Despesa */}
            <div className="space-y-3">
              <div className="flex items-center gap-2">
                <Checkbox
                  id="create-expense"
                  checked={createExpenseChecked}
                  onCheckedChange={(v) => setCreateExpenseChecked(!!v)}
                />
                <label
                  htmlFor="create-expense"
                  className="text-sm font-medium cursor-pointer"
                >
                  Criar despesa a partir deste contrato
                </label>
              </div>

              {createExpenseChecked && (
                <div className="space-y-3 pl-6">
                  <div className="space-y-1">
                    <label className="text-xs font-medium">
                      Categoria da Despesa
                    </label>
                    <Select
                      value={expenseCategory}
                      onValueChange={setExpenseCategory}
                    >
                      <SelectTrigger className="h-8 text-sm">
                        <SelectValue placeholder="Selecione uma categoria" />
                      </SelectTrigger>
                      <SelectContent>
                        {categories.map((c) => (
                          <SelectItem key={c.uuid} value={c.uuid}>
                            {c.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    <div className="space-y-1">
                      <label className="text-xs font-medium">
                        Nº de Parcelas
                      </label>
                      <Input
                        type="number"
                        min={1}
                        value={numInstallments}
                        onChange={(e) =>
                          setNumInstallments(Math.max(1, Number(e.target.value) || 1))
                        }
                        className="h-8 text-sm"
                      />
                    </div>
                    <div className="space-y-1">
                      <label className="text-xs font-medium">
                        Venc. 1ª Parcela
                      </label>
                      <Input
                        type="date"
                        value={firstDueDate}
                        onChange={(e) => setFirstDueDate(e.target.value)}
                        className="h-8 text-sm"
                      />
                    </div>
                  </div>
                </div>
              )}
            </div>

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
                {isCreating ? (
                  <Loader2 className="mr-2 size-4 animate-spin" />
                ) : null}
                Criar Contrato
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
});
