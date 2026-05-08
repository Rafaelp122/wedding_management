import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { getWeddingStatusInfo } from "../utils/weddingStatus";
import type { WeddingOut } from "@/api/generated/v1/models/weddingOut";
import { EditWeddingDialog } from "./EditWeddingDialog";
import { DeleteWeddingDialog } from "./DeleteWeddingDialog";

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import {
  DropdownMenuItem,
  DropdownMenuSeparator,
} from "@/components/ui/dropdown-menu";
import { TableRowActionsMenu } from "@/features/shared/components/TableRowActionsMenu";
import { formatDateBR } from "@/features/shared/utils/formatters";
import { Eye, Edit, Trash2 } from "lucide-react";

interface WeddingsTableProps {
  weddings: WeddingOut[];
  onRefetch: () => void;
}

export function WeddingsTable({ weddings, onRefetch }: WeddingsTableProps) {
  const navigate = useNavigate();
  const [editingWedding, setEditingWedding] = useState<WeddingOut | null>(null);
  const [deletingWedding, setDeletingWedding] = useState<WeddingOut | null>(
    null,
  );

  return (
    <>
      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Noivos</TableHead>
              <TableHead>Data</TableHead>
              <TableHead>Local</TableHead>
              <TableHead>Convidados</TableHead>
              <TableHead>Status</TableHead>
              <TableHead className="w-20">Ações</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {weddings.map((wedding) => {
              const statusInfo = getWeddingStatusInfo(wedding.status);

              return (
                <TableRow
                  key={wedding.uuid}
                  className="cursor-pointer"
                  onClick={() => navigate(`/weddings/${wedding.uuid}`)}
                >
                  <TableCell className="font-medium">
                    {wedding.groom_name} & {wedding.bride_name}
                  </TableCell>
                  <TableCell>
                    {formatDateBR(wedding.date, {
                      day: "2-digit",
                      month: "long",
                      year: "numeric",
                    })}
                  </TableCell>
                  <TableCell>{wedding.location}</TableCell>
                  <TableCell>
                    {wedding.expected_guests ?? (
                      <span className="text-muted-foreground">—</span>
                    )}
                  </TableCell>
                  <TableCell>
                    <Badge variant={statusInfo.variant}>
                      {statusInfo.label}
                    </Badge>
                  </TableCell>
                  <TableCell onClick={(event) => event.stopPropagation()}>
                    <TableRowActionsMenu>
                      <DropdownMenuItem asChild>
                        <Link to={`/weddings/${wedding.uuid}`}>
                          <Eye className="mr-2 size-4" />
                          Ver Detalhes
                        </Link>
                      </DropdownMenuItem>
                      <DropdownMenuItem onClick={() => setEditingWedding(wedding)}>
                        <Edit className="mr-2 size-4" />
                        Editar
                      </DropdownMenuItem>
                      <DropdownMenuSeparator />
                      <DropdownMenuItem
                        className="text-destructive focus:text-destructive"
                        onClick={() => setDeletingWedding(wedding)}
                      >
                        <Trash2 className="mr-2 size-4" />
                        Deletar
                      </DropdownMenuItem>
                    </TableRowActionsMenu>
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </div>

      {/* Dialogs */}
      {editingWedding && (
        <EditWeddingDialog
          wedding={editingWedding}
          open={!!editingWedding}
          onOpenChange={(open) => !open && setEditingWedding(null)}
          onSuccess={() => {
            onRefetch();
            setEditingWedding(null);
          }}
        />
      )}

      {deletingWedding && (
        <DeleteWeddingDialog
          wedding={deletingWedding}
          open={!!deletingWedding}
          onOpenChange={(open) => !open && setDeletingWedding(null)}
          onSuccess={() => {
            onRefetch();
            setDeletingWedding(null);
          }}
        />
      )}
    </>
  );
}
