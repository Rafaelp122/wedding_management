import { memo } from "react";
import { Edit, Trash2 } from "lucide-react";

import type { SupplierOut } from "@/api/generated/v1/models/supplierOut";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  DropdownMenuItem,
  DropdownMenuSeparator,
} from "@/components/ui/dropdown-menu";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { TableRowActionsMenu } from "@/components/table-row-actions-menu";
import { formatDateBR } from "@/lib/formatters";

interface SuppliersTableProps {
  suppliers: SupplierOut[];
  onEdit: (supplier: SupplierOut) => void;
  onDelete: (supplier: SupplierOut) => void;
  onDetail?: (uuid: string) => void;
}

export const SuppliersTable = memo(function SuppliersTable({
  suppliers,
  onEdit,
  onDelete,
  onDetail,
}: SuppliersTableProps) {

  return (
    <div className="rounded-md border">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Fornecedor</TableHead>
            <TableHead>E-mail</TableHead>
            <TableHead>Telefone</TableHead>
            <TableHead>CNPJ</TableHead>
            <TableHead>Status</TableHead>
            <TableHead>Cadastrado em</TableHead>
            <TableHead className="w-20">Ações</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {suppliers.map((supplier) => (
            <TableRow
              key={supplier.uuid}
              className={onDetail ? "hover:bg-muted/50" : ""}
            >
              <TableCell className="font-medium truncate max-w-40 p-0">
                <Tooltip>
                  <TooltipTrigger asChild>
                    <Button
                      variant="link"
                      className="h-auto w-full justify-start px-4 py-3 text-sm font-medium text-foreground hover:no-underline"
                      onClick={() => onDetail?.(supplier.uuid)}
                    >
                      <span className="truncate">{supplier.name}</span>
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent>{supplier.name}</TooltipContent>
                </Tooltip>
              </TableCell>
              <TableCell>{supplier.email || "—"}</TableCell>
              <TableCell>{supplier.phone || "—"}</TableCell>
              <TableCell>{supplier.cnpj || "—"}</TableCell>
              <TableCell>
                <Badge variant={supplier.is_active ? "secondary" : "outline"}>
                  {supplier.is_active ? "Ativo" : "Inativo"}
                </Badge>
              </TableCell>
              <TableCell>{formatDateBR(supplier.created_at)}</TableCell>
              <TableCell onClick={(event) => event.stopPropagation()}>
                <TableRowActionsMenu>
                  <DropdownMenuItem onClick={() => onEdit(supplier)}>
                    <Edit className="mr-2 h-4 w-4" />
                    Editar
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem
                    className="text-destructive focus:text-destructive"
                    onClick={() => onDelete(supplier)}
                  >
                    <Trash2 className="mr-2 h-4 w-4" />
                    Deletar
                  </DropdownMenuItem>
                </TableRowActionsMenu>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
})
