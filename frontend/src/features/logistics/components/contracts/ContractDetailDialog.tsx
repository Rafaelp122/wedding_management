import { memo } from "react";
import { MessageCircle, Mail, Plus } from "lucide-react";

import type { ContractOut } from "@/api/generated/v1/models/contractOut";
import {
  useLogisticsItemsList,
  useLogisticsContractsRead,
  useLogisticsContractsList,
} from "@/api/generated/v1/endpoints/logistics/logistics";
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
} from "@/features/logistics/constants";
import { ContractDocumentSection } from "./ContractDocumentSection";
import { ContractItemsSection } from "./ContractItemsSection";

interface ContractDetailDialogProps {
  contractUuid: string | null;
  weddingUuid: string;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onExpenseClick?: (expenseUuid: string | null) => void;
  onGenerateExpense?: (contract: ContractOut) => void;
  onSupplierClick?: (supplierUuid: string) => void;
  onCreateAddendum?: (parentUuid: string) => void;
}

export const ContractDetailDialog = memo(function ContractDetailDialog({
  contractUuid,
  weddingUuid,
  open,
  onOpenChange,
  onExpenseClick,
  onGenerateExpense,
  onSupplierClick,
  onCreateAddendum,
}: ContractDetailDialogProps) {
  const { data: contractResponse, isLoading: isContractLoading } =
    useLogisticsContractsRead(contractUuid ?? "", {
      query: { enabled: !!contractUuid, staleTime: 0 },
    });
  const contract = contractResponse?.data;

  const { data: itemsResponse, isLoading: isItemsLoading } =
    useLogisticsItemsList(
      { contract_id: contractUuid ?? "" },
      { query: { enabled: !!contractUuid } },
    );

  const { data: allContractsResponse } = useLogisticsContractsList({
    wedding_id: weddingUuid,
  });
  const addendums =
    allContractsResponse?.data?.items?.filter(
      (c) => c.parent === contractUuid,
    ) ?? [];

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
                    {onSupplierClick ? (
                      <button
                        type="button"
                        className="font-medium text-primary hover:underline cursor-pointer"
                        onClick={() => onSupplierClick(contract.supplier)}
                      >
                        {contract.supplier_name ||
                          contract.supplier.substring(0, 8)}
                      </button>
                    ) : (
                      <span className="font-medium text-foreground">
                        {contract.supplier_name ||
                          contract.supplier.substring(0, 8)}
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
                  <p className="text-sm">
                    Valor Total:{" "}
                    <span className="font-medium text-foreground">
                      R$ {formatCurrencyBR(Number(contract.total_amount))}
                    </span>
                  </p>
                  {contract.description && (
                    <p className="text-sm text-muted-foreground pt-1">
                      {contract.description}
                    </p>
                  )}
                </div>
              </DialogDescription>
            </DialogHeader>

            <div className="space-y-4">
              <Separator />

              <ContractDocumentSection
                contractUuid={contractUuid!}
                hasFile={contract.has_file ?? false}
                fileName={contract.file_name}
              />

              <Separator />

              <ContractItemsSection
                weddingUuid={weddingUuid}
                contractUuid={contractUuid!}
                items={itemsResponse?.data?.items ?? []}
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

              {addendums.length > 0 && (
                <div>
                  <Separator />
                  <h4 className="text-sm font-semibold mb-2 mt-3">Aditivos</h4>
                  <div className="rounded-md border">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="border-b bg-muted/50">
                          <th className="text-left px-3 py-2 font-medium text-xs">
                            Nome
                          </th>
                          <th className="text-right px-3 py-2 font-medium text-xs w-24">
                            Valor
                          </th>
                          <th className="text-center px-3 py-2 font-medium text-xs w-20">
                            Status
                          </th>
                        </tr>
                      </thead>
                      <tbody>
                        {addendums.map((a) => (
                          <tr key={a.uuid} className="border-b last:border-0">
                            <td className="px-3 py-2 truncate max-w-[180px]">
                              {a.name || a.description || "Aditivo"}
                            </td>
                            <td className="px-3 py-2 text-right">
                              R$ {formatCurrencyBR(Number(a.total_amount))}
                            </td>
                            <td className="px-3 py-2 text-center">
                              <Badge
                                className={`text-[10px] h-5 ${STATUS_STYLES[a.status] || ""}`}
                              >
                                {STATUS_LABELS[a.status] || a.status}
                              </Badge>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {onCreateAddendum && (
                <div className="mt-2">
                  <Button
                    variant="outline"
                    size="sm"
                    className="h-7 text-xs w-full"
                    onClick={() => onCreateAddendum(contractUuid!)}
                  >
                    <Plus className="size-3 mr-1" />
                    Criar Aditivo
                  </Button>
                </div>
              )}
            </div>
          </>
        )}
      </DialogContent>
    </Dialog>
  );
});
