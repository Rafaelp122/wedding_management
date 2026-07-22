import { memo } from "react";
import { AlertTriangle, Loader2 } from "lucide-react";

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

import { FormInput, FormSelect, FormNumber, FormTextarea } from "@/components/form-fields";
import { ContractItemDrafts } from "./ContractItemDrafts";
import { ContractCreateExpenseFields } from "./ContractCreateExpenseFields";
import { useContractUploadForm } from "../../hooks/useContractUploadForm";

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
  const {
    form,
    suppliers,
    existingContracts,
    categories,
    setSelectedFile,
    itemDrafts,
    setItemDrafts,
    handleExpenseChange,
    isSubmitting,
    onSubmit,
    handleOpenChange,
  } = useContractUploadForm({
    weddingUuid,
    prefilledParentUuid,
    onOpenChange,
    onSuccess,
  });

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
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
              onExpenseChange={handleExpenseChange}
            />

            <DialogFooter>
              <Button
                type="button"
                variant="outline"
                onClick={() => handleOpenChange(false)}
                disabled={isSubmitting}
              >
                Cancelar
              </Button>
              <Button type="submit" disabled={isSubmitting}>
                {isSubmitting && <Loader2 className="mr-2 size-4 animate-spin" />}
                Criar Contrato
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
});
