import type { ContractOut } from "@/api/generated/v1/models/contractOut";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { formatCurrencyBR, formatDateBR } from "@/features/shared/utils/formatters";

interface WeddingVendorsTableProps {
  contracts: ContractOut[];
}

export function WeddingVendorsTable({ contracts }: WeddingVendorsTableProps) {
  if (contracts.length === 0) {
    return (
      <div className="text-center py-6 text-muted-foreground border rounded-md">
        <p className="text-sm">Nenhum contrato de fornecedor vinculado a este evento.</p>
      </div>
    );
  }

  return (
    <div className="rounded-md border">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Fornecedor (Ref)</TableHead>
            <TableHead>Descrição</TableHead>
            <TableHead>Status</TableHead>
            <TableHead>Assinatura</TableHead>
            <TableHead className="text-right">Valor Total</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {contracts.map((contract) => (
            <TableRow key={contract.uuid}>
              <TableCell className="font-medium text-xs text-muted-foreground uppercase flex gap-1">
                {contract.supplier.substring(0, 8)}
                {/* O id do supplier será substituído pelo nome se integrarmos o Supplier endpoint mais a fundo ou ajustarmos a API para expor o nome */}
              </TableCell>
              <TableCell className="max-w-[200px] truncate" title={contract.description}>
                {contract.description || "N/A"}
              </TableCell>
              <TableCell>
                <Badge variant={contract.status === "ACTIVE" ? "default" : "secondary"}>
                  {contract.status}
                </Badge>
              </TableCell>
              <TableCell>
                {contract.signed_date
                  ? formatDateBR(contract.signed_date)
                  : "N/A"
                }
              </TableCell>
              <TableCell className="text-right font-medium">
                R$ {formatCurrencyBR(Number(contract.total_amount))}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
