import { useState } from "react";
import { MessageCircle, Mail, MoreHorizontal } from "lucide-react";

import type { ContractOut } from "@/api/generated/v1/models/contractOut";
import { formatCurrencyBR, formatDateBR } from "@/lib/formatters";
import {
  useLogisticsContractsDelete,
} from "@/api/generated/v1/endpoints/logistics/logistics";
import { createMutationCallbacks } from "@/hooks/use-mutation-toast";

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Button } from "@/components/ui/button";
import { ConfirmDeleteDialog } from "@/components/ui/confirm-delete-dialog";
import { STATUS_STYLES, STATUS_LABELS } from "@/features/logistics/constants";

interface WeddingVendorsTableProps {
  contracts: ContractOut[];
  isAddendum?: (contract: ContractOut) => boolean;
  onDetail?: (uuid: string) => void;
  onEdit?: (contract: ContractOut) => void;
  onGenerateExpense?: (contract: ContractOut) => void;
  onRefresh?: () => void;
}

export function WeddingVendorsTable({
  contracts,
  isAddendum,
  onDetail,
  onEdit,
  onGenerateExpense,
  onRefresh,
}: WeddingVendorsTableProps) {
  const [deletingContract, setDeletingContract] = useState<ContractOut | null>(null);
  const { mutate: deleteContract, isPending: isDeleting } =
    useLogisticsContractsDelete();

  const handleDelete = () => {
    if (!deletingContract) return;
    deleteContract(
      { uuid: deletingContract.uuid },
      createMutationCallbacks({
        successMsg: "Contrato deletado com sucesso!",
        fallbackErrorMsg: "Erro ao deletar contrato.",
        onSuccess: () => {
          setDeletingContract(null);
          onRefresh?.();
        },
      }),
    );
  };

  if (contracts.length === 0) {
    return (
      <div className="text-center py-6 text-muted-foreground border rounded-md">
        <p className="text-sm">Nenhum contrato de fornecedor vinculado a este evento.</p>
      </div>
    );
  }

  const hasActions = onEdit || onGenerateExpense;

  return (
    <>
      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Fornecedor</TableHead>
              <TableHead>Descrição</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Assinatura</TableHead>
              <TableHead className="text-right">Valor Total</TableHead>
              {hasActions && <TableHead className="w-10" />}
            </TableRow>
          </TableHeader>
          <TableBody>
            {contracts.map((contract) => {
              const addendum = isAddendum?.(contract) ?? false;
              const progressLabel = contract.has_linked_expense
                ? `${contract.progress_percent ?? 0}% pago`
                : undefined;

              return (
                <TableRow
                  key={contract.uuid}
                  className={`${addendum ? "bg-muted/50" : ""} ${onDetail ? "cursor-pointer hover:bg-muted/50" : ""}`}
                  onClick={() => onDetail?.(contract.uuid)}
                >
                  <TableCell className="font-medium">
                    <div className="flex flex-col gap-0.5">
                      <div className="flex items-center gap-2">
                        {addendum && (
                          <span className="text-muted-foreground text-xs">↳ Aditivo</span>
                        )}
                        <span>
                          {contract.name || contract.description || contract.supplier_name || contract.supplier.substring(0, 8)}
                        </span>
                      </div>
                      <span className="flex gap-1 items-center">
                        <span className="text-xs text-muted-foreground">
                          {contract.supplier_name || contract.supplier.substring(0, 8)}
                        </span>
                        {contract.supplier_phone && (
                          <a
                            href={`https://wa.me/55${contract.supplier_phone.replace(/\D/g, "")}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-green-600 hover:text-green-800"
                            title="WhatsApp"
                            onClick={(e) => e.stopPropagation()}
                          >
                            <MessageCircle className="size-3.5" />
                          </a>
                        )}
                        {contract.supplier_email && (
                          <a
                            href={`mailto:${contract.supplier_email}`}
                            className="text-blue-600 hover:text-blue-800"
                            title="Email"
                            onClick={(e) => e.stopPropagation()}
                          >
                            <Mail className="size-3.5" />
                          </a>
                        )}
                      </span>
                    </div>
                  </TableCell>
                  <TableCell className="max-w-[200px] truncate" title={contract.description}>
                    {contract.description || "N/A"}
                  </TableCell>
                  <TableCell>
                    <Badge className={STATUS_STYLES[contract.status] || ""}>
                      {STATUS_LABELS[contract.status] || contract.status}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    {contract.signed_date ? formatDateBR(contract.signed_date) : "N/A"}
                  </TableCell>
                  <TableCell className="text-right font-medium whitespace-nowrap">
                    <div>R$ {formatCurrencyBR(Number(contract.total_amount))}</div>
                    {contract.has_linked_expense && (
                      <div className="flex items-center gap-1 mt-1">
                        <Progress
                          value={contract.progress_percent || 0}
                          className="h-1.5 w-20"
                        />
                        <span className="text-[10px] text-muted-foreground">
                          {progressLabel}
                        </span>
                      </div>
                    )}
                  </TableCell>
                  {hasActions && (
                    <TableCell>
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button
                            variant="ghost"
                            size="icon"
                            className="size-8"
                            onClick={(e) => e.stopPropagation()}
                          >
                            <MoreHorizontal className="size-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end" onClick={(e) => e.stopPropagation()}>
                          {onEdit && (
                            <DropdownMenuItem onClick={() => onEdit(contract)}>
                              Editar
                            </DropdownMenuItem>
                          )}
                          {onGenerateExpense && (
                            <DropdownMenuItem onClick={() => onGenerateExpense(contract)}>
                              Gerar Despesa
                            </DropdownMenuItem>
                          )}
                          <DropdownMenuItem
                            className="text-destructive"
                            onClick={() => setDeletingContract(contract)}
                          >
                            Excluir
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </TableCell>
                  )}
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </div>

      <ConfirmDeleteDialog
        open={!!deletingContract}
        onOpenChange={(open) => {
          if (!open) setDeletingContract(null);
        }}
        title="Excluir Contrato"
        description="Esta ação removerá permanentemente o contrato e seus vínculos."
        itemName={deletingContract?.supplier_name || deletingContract?.description || ""}
        consequences={[
          "Itens logísticos órfãos serão desvinculados",
          "Despesas vinculadas perderão a referência ao contrato",
          "Parcelas já pagas serão preservadas na despesa",
        ]}
        onConfirm={handleDelete}
        isPending={isDeleting}
      />
    </>
  );
}
