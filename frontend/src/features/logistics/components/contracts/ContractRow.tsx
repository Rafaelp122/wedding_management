import { memo, useState } from "react";
import { MessageCircle, Mail, MoreHorizontal } from "lucide-react";
import type { ContractOut } from "@/api/generated/v1/models/contractOut";
import { formatCurrencyBR, formatDateBR } from "@/features/shared/utils/formatters";
import {
  useLogisticsContractsDelete,
} from "@/api/generated/v1/endpoints/logistics/logistics";
import { toast } from "sonner";
import { getApiErrorInfo } from "@/api/error-utils";

import {
  TableCell,
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

const STATUS_STYLES: Record<string, string> = {
  DRAFT: "bg-gray-100 text-gray-700",
  PENDING: "bg-yellow-100 text-yellow-800",
  SIGNED: "bg-green-100 text-green-800",
  CANCELED: "bg-red-100 text-red-800",
};

const STATUS_LABELS: Record<string, string> = {
  DRAFT: "Rascunho",
  PENDING: "Pendente",
  SIGNED: "Assinado",
  CANCELED: "Cancelado",
};

interface ContractRowProps {
  contract: ContractOut;
  isAddendum?: boolean;
  onDetail: (uuid: string) => void;
  onEdit: (contract: ContractOut) => void;
  onGenerateExpense: (contract: ContractOut) => void;
  onRefresh: () => void;
}

export const ContractRow = memo(function ContractRow({
  contract,
  isAddendum = false,
  onDetail,
  onEdit,
  onGenerateExpense,
  onRefresh,
}: ContractRowProps) {
  const [deletingContract, setDeletingContract] = useState<ContractOut | null>(null);
  const { mutate: deleteContract, isPending: isDeleting } =
    useLogisticsContractsDelete();

  let progressLabel = "0%";
  if (contract.has_linked_expense && contract.progress_percent !== undefined) {
    progressLabel = `${contract.progress_percent}% pago`;
  } else if (contract.has_linked_expense) {
    progressLabel = "Vinculado";
  }

  const handleDelete = () => {
    if (!deletingContract) return;
    deleteContract(
      { uuid: deletingContract.uuid },
      {
        onSuccess: () => {
          toast.success("Contrato deletado com sucesso!");
          setDeletingContract(null);
          onRefresh();
        },
        onError: (error) => {
          const { message } = getApiErrorInfo(error, "Erro ao deletar contrato.");
          toast.error(message);
        },
      },
    );
  };

  return (
    <>
      <TableRow
        key={contract.uuid}
        className={`${isAddendum ? "bg-muted/50" : ""} cursor-pointer hover:bg-muted/50`}
        onClick={() => onDetail(contract.uuid)}
      >
        <TableCell className="font-medium">
          <div className="flex flex-col gap-0.5">
            <div className="flex items-center gap-2">
              {isAddendum && (
                <span className="text-muted-foreground text-xs">↳ Aditivo</span>
              )}
              <span>{contract.name || contract.description || contract.supplier_name || contract.supplier.substring(0, 8)}</span>
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
                >
                  <MessageCircle className="size-3.5" />
                </a>
              )}
              {contract.supplier_email && (
                <a
                  href={`mailto:${contract.supplier_email}`}
                  className="text-blue-600 hover:text-blue-800"
                  title="Email"
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
              <DropdownMenuItem onClick={() => onEdit(contract)}>
                Editar
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => onGenerateExpense(contract)}>
                Gerar Despesa
              </DropdownMenuItem>
              <DropdownMenuItem
                className="text-destructive"
                onClick={() => setDeletingContract(contract)}
              >
                Excluir
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </TableCell>
      </TableRow>

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
});
