import { memo } from "react";
import { MessageCircle, Mail } from "lucide-react";

import type { ContractOut } from "@/api/generated/v1/models/contractOut";
import type { ContractAddendumOut } from "@/api/generated/v1/models/contractAddendumOut";
import type { ItemOut } from "@/api/generated/v1/models/itemOut";
import { formatCurrencyBR, formatDateBR } from "@/lib/formatters";

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Separator } from "@/components/ui/separator";

import {
  STATUS_STYLES,
  STATUS_LABELS,
} from "@/features/contracts/constants";
import { ContractDocumentSection } from "./ContractDocumentSection";
import { ContractItemsSection } from "./ContractItemsSection";
import { ContractAddendumList } from "./ContractAddendumList";

export interface ContractDetailDialogViewProps {
  contractUuid: string | null;
  weddingUuid: string;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  contract: ContractOut | null | undefined;
  isContractLoading: boolean;
  items: ItemOut[];
  isItemsLoading: boolean;
  addendums: ContractAddendumOut[];
  onExpenseClick?: (expenseUuid: string | null) => void;
  onGenerateExpense?: (contract: ContractOut) => void;
  onSupplierClick?: (supplierUuid: string) => void;
  onCreateAddendum?: (parentUuid: string) => void;
  onSignAddendum?: (addendum: ContractAddendumOut) => void;
  onSendToPending?: (contract: ContractOut) => void;
  onSign?: (contract: ContractOut) => void;
  onCancel?: (contract: ContractOut) => void;
  onRevertToDraft?: (contract: ContractOut) => void;
  isTransitionPending?: boolean;
}

export const ContractDetailDialogView = memo(function ContractDetailDialogView({
  contractUuid,
  weddingUuid,
  open,
  onOpenChange,
  contract,
  isContractLoading,
  items,
  isItemsLoading,
  addendums,
  onExpenseClick,
  onGenerateExpense,
  onSupplierClick,
  onCreateAddendum,
  onSignAddendum,
  onSendToPending,
  onSign,
  onCancel,
  onRevertToDraft,
  isTransitionPending,
}: ContractDetailDialogViewProps) {
  const baseAmount = contract?.base_amount ?? contract?.total_amount ?? "0.00";
  const addendumsTotal =
    contract?.addendums_total ?? contract?.addendums_total_amount ?? "0.00";
  const effectiveAmount =
    contract?.effective_amount ??
    contract?.total_amount_with_addendums ??
    baseAmount;

  const hasAddendums =
    (contract?.addendums_count ?? 0) > 0 ||
    addendums.length > 0 ||
    Number(addendumsTotal) > 0;
  const addendumsDisplayCount = contract?.addendums_count ?? addendums.length;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[560px] max-h-[85vh] overflow-y-auto">
        {isContractLoading ? (
          <>
            <DialogTitle className="sr-only">Carregando contrato...</DialogTitle>
            <DialogDescription className="sr-only">
              Carregando contrato...
            </DialogDescription>
            <div className="space-y-3 py-4">
              <Skeleton className="h-6 w-48" />
              <Skeleton className="h-4 w-32" />
              <Skeleton className="h-4 w-40" />
            </div>
          </>
        ) : !contract ? (
          <DialogHeader>
            <DialogTitle>Contrato não encontrado</DialogTitle>
            <DialogDescription>
              Os dados deste contrato não estão disponíveis.
            </DialogDescription>
          </DialogHeader>
        ) : (
          <>
            <DialogHeader>
              <DialogTitle className="flex items-center justify-between pr-8">
                <span className="truncate">
                  {contract.name || contract.description || "Contrato"}
                </span>
                <Badge className={STATUS_STYLES[contract.status] || ""}>
                  {STATUS_LABELS[contract.status] || contract.status}
                </Badge>
              </DialogTitle>
              <DialogDescription asChild>
                <div className="space-y-1 pt-1">
                  <p className="text-sm">
                    Fornecedor:{" "}
                    {onSupplierClick && contract.supplier ? (
                      <button
                        type="button"
                        className="font-medium text-primary hover:underline cursor-pointer"
                        onClick={() => onSupplierClick(contract.supplier as string)}
                      >
                        {contract.supplier_name ||
                          (contract.supplier
                            ? contract.supplier.substring(0, 8)
                            : "—")}
                      </button>
                    ) : (
                      <span className="font-medium text-foreground">
                        {contract.supplier_name ||
                          (contract.supplier
                            ? contract.supplier.substring(0, 8)
                            : "—")}
                      </span>
                    )}
                    <span className="inline-flex gap-1 ml-1">
                      {contract.supplier_phone && (
                        <a
                          href={`https://wa.me/55${contract.supplier_phone.replace(/\D/g, "")}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-green-600 hover:text-green-800"
                        >
                          <MessageCircle className="size-3.5" />
                        </a>
                      )}
                      {contract.supplier_email && (
                        <a
                          href={`mailto:${contract.supplier_email}`}
                          className="text-blue-600 hover:text-blue-800"
                        >
                          <Mail className="size-3.5" />
                        </a>
                      )}
                    </span>
                  </p>
                  {contract.signed_date && (
                    <p className="text-sm">
                      Assinatura:{" "}
                      <span className="font-medium text-foreground">
                        {formatDateBR(contract.signed_date)}
                      </span>
                    </p>
                  )}
                  {hasAddendums ? (
                    <div className="rounded-md bg-muted/40 p-2.5 space-y-1 text-sm border mt-1.5">
                      <div className="flex justify-between text-muted-foreground">
                        <span>Valor Base:</span>
                        <span className="font-medium text-foreground">
                          R$ {formatCurrencyBR(Number(baseAmount))}
                        </span>
                      </div>
                      <div className="flex justify-between text-muted-foreground">
                        <span>
                          Total em Aditivos{addendumsDisplayCount > 0 ? ` (${addendumsDisplayCount})` : ""}:
                        </span>
                        <span className="font-medium text-foreground">
                          + R$ {formatCurrencyBR(Number(addendumsTotal))}
                        </span>
                      </div>
                      <Separator className="my-1" />
                      <div className="flex justify-between font-semibold text-foreground pt-0.5">
                        <span>Valor Efetivo Final:</span>
                        <span className="text-primary">
                          R$ {formatCurrencyBR(Number(effectiveAmount))}
                        </span>
                      </div>
                    </div>
                  ) : (
                    <p className="text-sm">
                      Valor Base:{" "}
                      <span className="font-medium text-foreground">
                        R$ {formatCurrencyBR(Number(baseAmount))}
                      </span>
                    </p>
                  )}
                  {contract.description && (
                    <p className="text-sm text-muted-foreground pt-1">
                      {contract.description}
                    </p>
                  )}
                </div>
              </DialogDescription>
            </DialogHeader>

            <div className="flex flex-wrap gap-2 pt-1 pb-1">
              {contract.status === "DRAFT" && (
                <>
                  {onSendToPending && (
                    <Button
                      size="sm"
                      className="h-8 text-xs"
                      onClick={() => onSendToPending(contract)}
                      disabled={isTransitionPending}
                    >
                      Enviar para Assinatura
                    </Button>
                  )}
                  {onCancel && (
                    <Button
                      variant="outline"
                      size="sm"
                      className="h-8 text-xs text-destructive hover:bg-destructive/10"
                      onClick={() => onCancel(contract)}
                      disabled={isTransitionPending}
                    >
                      Cancelar Contrato
                    </Button>
                  )}
                </>
              )}

              {contract.status === "PENDING" && (
                <>
                  {onSign && (
                    <Button
                      size="sm"
                      className="h-8 text-xs"
                      onClick={() => onSign(contract)}
                      disabled={isTransitionPending}
                    >
                      Formalizar Assinatura
                    </Button>
                  )}
                  {onRevertToDraft && (
                    <Button
                      variant="outline"
                      size="sm"
                      className="h-8 text-xs"
                      onClick={() => onRevertToDraft(contract)}
                      disabled={isTransitionPending}
                    >
                      Devolver para Rascunho
                    </Button>
                  )}
                  {onCancel && (
                    <Button
                      variant="outline"
                      size="sm"
                      className="h-8 text-xs text-destructive hover:bg-destructive/10"
                      onClick={() => onCancel(contract)}
                      disabled={isTransitionPending}
                    >
                      Cancelar Contrato
                    </Button>
                  )}
                </>
              )}

              {contract.status === "SIGNED" && (
                <>
                  {onCancel && (
                    <Button
                      variant="outline"
                      size="sm"
                      className="h-8 text-xs text-destructive hover:bg-destructive/10"
                      onClick={() => onCancel(contract)}
                      disabled={isTransitionPending}
                    >
                      Distratar / Cancelar
                    </Button>
                  )}
                </>
              )}

              {contract.status === "CANCELED" && (
                <>
                  {onRevertToDraft && (
                    <Button
                      variant="outline"
                      size="sm"
                      className="h-8 text-xs"
                      onClick={() => onRevertToDraft(contract)}
                      disabled={isTransitionPending}
                    >
                      Reabrir como Rascunho
                    </Button>
                  )}
                </>
              )}
            </div>

            <div className="space-y-4">
              <Separator />

              <ContractDocumentSection
                contractUuid={contractUuid!}
                hasFile={contract.has_file ?? false}
                fileName={contract.file_name}
                weddingUuid={weddingUuid}
              />

              <Separator />

              <ContractItemsSection
                weddingUuid={weddingUuid}
                contractUuid={contractUuid!}
                items={items}
                isLoading={isItemsLoading}
              />

              <Separator />

              <div>
                <h4 className="text-sm font-semibold mb-2">Despesa Vinculada</h4>
                {contract.has_linked_expense ? (
                  <div className="rounded-lg border bg-muted/30 p-3">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div>
                          <p className="text-sm font-medium">
                            R$ {formatCurrencyBR(Number(contract.total_amount))}
                          </p>
                          <p className="text-xs text-muted-foreground">
                            {contract.progress_percent || 0}% pago
                          </p>
                        </div>
                        <Progress
                          value={contract.progress_percent || 0}
                          className="h-2 w-20"
                        />
                      </div>
                      <Button
                        variant="outline"
                        size="sm"
                        className="h-7 text-xs"
                        onClick={() =>
                          onExpenseClick?.(contract.expense_uuid ?? null)
                        }
                      >
                        Ver detalhes da despesa →
                      </Button>
                    </div>
                  </div>
                ) : (
                  <div className="rounded-lg border bg-muted/30 p-3">
                    <div className="flex items-center justify-between">
                      <p className="text-sm text-muted-foreground">
                        Nenhuma despesa vinculada a este contrato.
                      </p>
                      {onGenerateExpense && (
                        <Button
                          variant="outline"
                          size="sm"
                          className="h-7 text-xs"
                          onClick={() => onGenerateExpense(contract)}
                        >
                          Gerar Despesa
                        </Button>
                      )}
                    </div>
                  </div>
                )}
              </div>

              <Separator />

              <ContractAddendumList
                addendums={addendums}
                onSignAddendum={onSignAddendum}
                onCreateAddendum={
                  onCreateAddendum && contractUuid
                    ? () => onCreateAddendum(contractUuid)
                    : undefined
                }
              />
            </div>
          </>
        )}
      </DialogContent>
    </Dialog>
  );
});
