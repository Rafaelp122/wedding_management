import { useState } from "react";
import { Link } from "react-router-dom";
import type { WeddingOut } from "@/api/generated/v1/models";
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
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { MoreHorizontal, Eye, Edit, Trash2 } from "lucide-react";

interface WeddingsTableProps {
  weddings: WeddingOut[];
  onRefetch: () => void;
}

const STATUS_LABELS: Record<
  string,
  { label: string; variant: "default" | "secondary" | "destructive" }
> = {
  IN_PROGRESS: { label: "Em Andamento", variant: "default" },
  COMPLETED: { label: "Concluído", variant: "secondary" },
  CANCELED: { label: "Cancelado", variant: "destructive" },
};

export function WeddingsTable({ weddings, onRefetch }: WeddingsTableProps) {
  const [editingWedding, setEditingWedding] = useState<WeddingOut | null>(null);
  const [deletingWedding, setDeletingWedding] = useState<WeddingOut | null>(
    null,
  );

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("pt-BR", {
      day: "2-digit",
      month: "long",
      year: "numeric",
    });
  };

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
              const statusInfo =
                STATUS_LABELS[wedding.status] || STATUS_LABELS.IN_PROGRESS;

              return (
                <TableRow key={wedding.uuid}>
                  <TableCell className="font-medium">
                    {wedding.groom_name} & {wedding.bride_name}
                  </TableCell>
                  <TableCell>{formatDate(wedding.date)}</TableCell>
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
                  <TableCell>
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button variant="ghost" size="icon" className="h-8 w-8">
                          <MoreHorizontal className="h-4 w-4" />
                          <span className="sr-only">Abrir menu</span>
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuLabel>Ações</DropdownMenuLabel>
                        <DropdownMenuSeparator />
                        <DropdownMenuItem asChild>
                          <Link to={`/weddings/${wedding.uuid}`}>
                            <Eye className="mr-2 h-4 w-4" />
                            Ver Detalhes
                          </Link>
                        </DropdownMenuItem>
                        <DropdownMenuItem
                          onClick={() => setEditingWedding(wedding)}
                        >
                          <Edit className="mr-2 h-4 w-4" />
                          Editar
                        </DropdownMenuItem>
                        <DropdownMenuSeparator />
                        <DropdownMenuItem
                          className="text-destructive focus:text-destructive"
                          onClick={() => setDeletingWedding(wedding)}
                        >
                          <Trash2 className="mr-2 h-4 w-4" />
                          Deletar
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
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
