import { Edit, Trash2 } from "lucide-react";

import type { SupplierOut } from "@/api/generated/v1/models";
import { Badge } from "@/components/ui/badge";
import {
  DropdownMenuItem,
  DropdownMenuSeparator,
} from "@/components/ui/dropdown-menu";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { TableRowActionsMenu } from "@/features/shared/components/TableRowActionsMenu";
import { formatDateBR } from "@/features/shared/utils/formatters";

interface SuppliersTableProps {
  suppliers: SupplierOut[];
  onEdit: (supplier: SupplierOut) => void;
  onDelete: (supplier: SupplierOut) => void;
}

export function SuppliersTable({ suppliers, onEdit, onDelete }: SuppliersTableProps) {
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
            <TableRow key={supplier.uuid}>
              <TableCell className="font-medium">{supplier.name}</TableCell>
              <TableCell>{supplier.email || "—"}</TableCell>
              <TableCell>{supplier.phone || "—"}</TableCell>
              <TableCell>{supplier.cnpj || "—"}</TableCell>
              <TableCell>
                <Badge variant={supplier.is_active ? "secondary" : "outline"}>
                  {supplier.is_active ? "Ativo" : "Inativo"}
                </Badge>
              </TableCell>
              <TableCell>{formatDateBR(supplier.created_at)}</TableCell>
              <TableCell>
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
}
