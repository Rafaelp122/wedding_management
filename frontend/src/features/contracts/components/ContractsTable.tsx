import { memo } from "react";
import { Eye } from "lucide-react";
import type { ContractOut } from "@/api/generated/v1/models/contractOut";
import { formatCurrencyBR } from "@/lib/formatters";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { STATUS_STYLES, STATUS_LABELS } from "@/features/contracts/constants";

export interface ContractsTableProps {
  contracts: ContractOut[];
  weddingMap?: Record<string, string>;
  onViewDetails?: (contract: ContractOut) => void;
}

export const ContractsTable = memo(function ContractsTable({
  contracts,
  weddingMap,
  onViewDetails,
}: ContractsTableProps) {
  if (contracts.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-center">
        <p className="text-muted-foreground text-sm">
          Nenhum contrato encontrado com os filtros aplicados.
        </p>
      </div>
    );
  }

  return (
    <div className="rounded-md border overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b bg-muted/50 text-muted-foreground text-xs">
            <th className="text-left px-4 py-3 font-medium">Casamento</th>
            <th className="text-left px-4 py-3 font-medium">Fornecedor</th>
            <th className="text-left px-4 py-3 font-medium">Contrato</th>
            <th className="text-right px-4 py-3 font-medium">Valor Base</th>
            <th className="text-right px-4 py-3 font-medium">Aditivos</th>
            <th className="text-right px-4 py-3 font-medium">Valor Efetivo</th>
            <th className="text-center px-4 py-3 font-medium">Status</th>
            {onViewDetails && (
              <th className="text-center px-4 py-3 font-medium w-24">Ações</th>
            )}
          </tr>
        </thead>
        <tbody>
          {contracts.map((contract) => {
            const baseAmount = Number(
              contract.base_amount ?? contract.total_amount ?? 0,
            );
            const addendumsTotal = Number(
              contract.addendums_total ??
                contract.addendums_total_amount ??
                0,
            );
            const effectiveAmount = Number(
              contract.effective_amount ??
                contract.total_amount_with_addendums ??
                contract.total_amount ??
                0,
            );
            const weddingLabel =
              weddingMap?.[contract.wedding] ||
              contract.wedding.substring(0, 8);

            return (
              <tr
                key={contract.uuid}
                className="border-b last:border-0 hover:bg-muted/20 transition-colors"
              >
                <td className="px-4 py-3 font-medium text-foreground whitespace-nowrap">
                  {weddingLabel}
                </td>
                <td className="px-4 py-3 text-muted-foreground whitespace-nowrap">
                  {contract.supplier_name ||
                    (contract.supplier ? contract.supplier.substring(0, 8) : "Assessoria")}
                </td>
                <td className="px-4 py-3 max-w-[200px] truncate" title={contract.name || contract.description}>
                  {contract.name || contract.description || "Contrato"}
                </td>
                <td className="px-4 py-3 text-right whitespace-nowrap">
                  R$ {formatCurrencyBR(baseAmount)}
                </td>
                <td className="px-4 py-3 text-right whitespace-nowrap text-muted-foreground">
                  {addendumsTotal > 0
                    ? `+ R$ ${formatCurrencyBR(addendumsTotal)}`
                    : "R$ 0,00"}
                </td>
                <td className="px-4 py-3 text-right font-semibold text-foreground whitespace-nowrap">
                  R$ {formatCurrencyBR(effectiveAmount)}
                </td>
                <td className="px-4 py-3 text-center whitespace-nowrap">
                  <Badge
                    className={`text-[11px] font-medium ${STATUS_STYLES[contract.status] || ""}`}
                  >
                    {STATUS_LABELS[contract.status] || contract.status}
                  </Badge>
                </td>
                {onViewDetails && (
                  <td className="px-4 py-3 text-center whitespace-nowrap">
                    <Button
                      type="button"
                      variant="outline"
                      size="sm"
                      className="h-7 text-xs"
                      onClick={() => onViewDetails(contract)}
                    >
                      <Eye className="size-3.5 mr-1" />
                      Detalhes
                    </Button>
                  </td>
                )}
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
});
