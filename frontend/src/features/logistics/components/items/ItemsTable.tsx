import { memo, useState } from "react";
import { MoreHorizontal } from "lucide-react";

import type { ItemOut } from "@/api/generated/v1/models/itemOut";
import {
  useLogisticsItemsDelete,
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
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Button } from "@/components/ui/button";
import { ConfirmDeleteDialog } from "@/components/ui/confirm-delete-dialog";
import { ITEM_STATUS_STYLES, ITEM_STATUS_LABELS } from "@/features/logistics/constants";

interface WeddingItemsTableProps {
  items: ItemOut[];
  onEdit?: (item: ItemOut) => void;
  onRefresh?: () => void;
}

export const WeddingItemsTable = memo(function WeddingItemsTable({ items, onEdit, onRefresh }: WeddingItemsTableProps) {
  const [deletingItem, setDeletingItem] = useState<ItemOut | null>(null);
  const { mutate: deleteItem, isPending: isDeleting } = useLogisticsItemsDelete();

  const handleDelete = () => {
    if (!deletingItem) return;
    deleteItem(
      { uuid: deletingItem.uuid },
      createMutationCallbacks({
        successMsg: "Item deletado com sucesso!",
        fallbackErrorMsg: "Erro ao deletar item.",
        onSuccess: () => {
          setDeletingItem(null);
          onRefresh?.();
        },
      }),
    );
  };

  if (items.length === 0) {
    return (
      <div className="text-center py-6 text-muted-foreground border rounded-md">
        <p className="text-sm">Nenhum item logístico planejado para este evento.</p>
      </div>
    );
  }

  const hasActions = !!onEdit;

  return (
    <>
      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Item</TableHead>
              <TableHead>Descrição</TableHead>
              <TableHead>Quantidade</TableHead>
              <TableHead>Status de Aquisição</TableHead>
              {hasActions && <TableHead className="w-10" />}
            </TableRow>
          </TableHeader>
          <TableBody>
            {items.map((item) => (
              <TableRow key={item.uuid}>
                <TableCell className="font-medium">{item.name}</TableCell>
                <TableCell className="max-w-[200px] truncate" title={item.description}>
                  {item.description || "N/A"}
                </TableCell>
                <TableCell>{item.quantity}</TableCell>
                <TableCell>
                  <Badge
                    className={`${ITEM_STATUS_STYLES[item.acquisition_status] || ""}`}
                  >
                    {ITEM_STATUS_LABELS[item.acquisition_status] || item.acquisition_status}
                  </Badge>
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
                          <DropdownMenuItem onClick={() => onEdit(item)}>
                            Editar
                          </DropdownMenuItem>
                        )}
                        <DropdownMenuItem
                          className="text-destructive"
                          onClick={() => setDeletingItem(item)}
                        >
                          Excluir
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </TableCell>
                )}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      <ConfirmDeleteDialog
        open={!!deletingItem}
        onOpenChange={(open) => {
          if (!open) setDeletingItem(null);
        }}
        title="Excluir Item"
        description="Esta ação removerá permanentemente o item e seus vínculos."
        itemName={deletingItem?.name || ""}
        onConfirm={handleDelete}
        isPending={isDeleting}
      />
    </>
  );
})
