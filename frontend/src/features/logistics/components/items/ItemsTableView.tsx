import { memo, useState } from "react";
import { MoreHorizontal } from "lucide-react";

import type { ItemOut } from "@/api/generated/v1/models/itemOut";

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
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ConfirmDeleteDialog } from "@/components/ui/confirm-delete-dialog";
import {
  ITEM_STATUS_STYLES,
  ITEM_STATUS_LABELS,
  SCOPE_STATUS_LABELS,
  SCOPE_STATUS_STYLES,
  DELIVERY_STATUS_LABELS,
  DELIVERY_STATUS_STYLES,
} from "@/features/logistics/constants";

export interface WeddingItemsTableViewProps {
  items: ItemOut[];
  onEdit?: (item: ItemOut) => void;
  onDelete: (item: ItemOut, onDone: () => void) => void;
  isDeleting: boolean;
  onStart: (item: ItemOut) => void;
  onComplete: (item: ItemOut) => void;
  onReopen: (item: ItemOut) => void;
  onRevertToPending: (item: ItemOut) => void;
  onConfirmDiscard: (item: ItemOut, reason: string, onDone: () => void) => void;
  isDiscarding: boolean;
  onInclude: (item: ItemOut) => void;
  onDeliver: (item: ItemOut) => void;
  onReturn: (item: ItemOut) => void;
}

export const WeddingItemsTableView = memo(function WeddingItemsTableView({
  items,
  onEdit,
  onDelete,
  isDeleting,
  onStart,
  onComplete,
  onReopen,
  onRevertToPending,
  onConfirmDiscard,
  isDiscarding,
  onInclude,
  onDeliver,
  onReturn,
}: WeddingItemsTableViewProps) {
  const [scopeFilter, setScopeFilter] = useState<string>("ALL");
  const [deletingItem, setDeletingItem] = useState<ItemOut | null>(null);
  const [discardingItem, setDiscardingItem] = useState<ItemOut | null>(null);
  const [rejectionReason, setRejectionReason] = useState("");

  const handleDelete = () => {
    if (!deletingItem) return;
    onDelete(deletingItem, () => setDeletingItem(null));
  };

  const handleConfirmDiscard = () => {
    if (!discardingItem || !rejectionReason.trim()) return;
    onConfirmDiscard(discardingItem, rejectionReason.trim(), () => {
      setDiscardingItem(null);
      setRejectionReason("");
    });
  };

  if (items.length === 0) {
    return (
      <div className="text-center py-6 text-muted-foreground border rounded-md">
        <p className="text-sm">Nenhum item logístico planejado para este evento.</p>
      </div>
    );
  }

  const filteredItems = items.filter((item) => {
    if (scopeFilter === "ALL") return true;
    return (item.scope_status || "INCLUDED") === scopeFilter;
  });

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <Tabs value={scopeFilter} onValueChange={setScopeFilter}>
          <TabsList>
            <TabsTrigger value="ALL">Todos ({items.length})</TabsTrigger>
            <TabsTrigger value="INCLUDED">
              Incluídos ({items.filter((i) => (i.scope_status || "INCLUDED") === "INCLUDED").length})
            </TabsTrigger>
            <TabsTrigger value="DESIRED">
              Desejados ({items.filter((i) => i.scope_status === "DESIRED").length})
            </TabsTrigger>
            <TabsTrigger value="DISCARDED">
              Descartados ({items.filter((i) => i.scope_status === "DISCARDED").length})
            </TabsTrigger>
          </TabsList>
        </Tabs>
      </div>

      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Item</TableHead>
              <TableHead>Descrição</TableHead>
              <TableHead>Quantidade</TableHead>
              <TableHead>Escopo</TableHead>
              <TableHead>Aquisição</TableHead>
              <TableHead>Entrega</TableHead>
              <TableHead className="w-10" />
            </TableRow>
          </TableHeader>
          <TableBody>
            {filteredItems.length === 0 ? (
              <TableRow>
                <TableCell colSpan={7} className="text-center py-6 text-muted-foreground">
                  Nenhum item encontrado para o filtro selecionado.
                </TableCell>
              </TableRow>
            ) : (
              filteredItems.map((item) => {
                const scope = item.scope_status || "INCLUDED";
                const delivery = item.delivery_status || "PENDING";
                const isDiscarded = scope === "DISCARDED";

                return (
                  <TableRow key={item.uuid} className={isDiscarded ? "opacity-75 bg-muted/20" : undefined}>
                    <TableCell className="font-medium">
                      <div className="flex flex-col">
                        <span>{item.name}</span>
                        {isDiscarded && item.rejection_reason && (
                          <span className="text-xs text-rose-600 dark:text-rose-400 mt-0.5">
                            Motivo: {item.rejection_reason}
                          </span>
                        )}
                      </div>
                    </TableCell>
                    <TableCell className="max-w-[200px] truncate" title={item.description}>
                      {item.description || "N/A"}
                    </TableCell>
                    <TableCell>{item.quantity}</TableCell>
                    <TableCell>
                      <Badge
                        variant="outline"
                        className={SCOPE_STATUS_STYLES[scope] || ""}
                      >
                        {SCOPE_STATUS_LABELS[scope] || scope}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Badge
                        className={ITEM_STATUS_STYLES[item.acquisition_status] || ""}
                      >
                        {ITEM_STATUS_LABELS[item.acquisition_status] || item.acquisition_status}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Badge
                        variant="outline"
                        className={DELIVERY_STATUS_STYLES[delivery] || ""}
                      >
                        {DELIVERY_STATUS_LABELS[delivery] || delivery}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button
                            variant="ghost"
                            size="icon"
                            className="size-8"
                            aria-label="Ações do item"
                            onClick={(e) => e.stopPropagation()}
                          >
                            <MoreHorizontal className="size-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end" onClick={(e) => e.stopPropagation()}>
                          {item.acquisition_status === "PENDING" && (
                            <DropdownMenuItem onClick={() => onStart(item)}>
                              Iniciar Aquisição
                            </DropdownMenuItem>
                          )}
                          {item.acquisition_status === "IN_PROGRESS" && (
                            <>
                              <DropdownMenuItem onClick={() => onComplete(item)}>
                                Marcar como Concluído
                              </DropdownMenuItem>
                              <DropdownMenuItem onClick={() => onRevertToPending(item)}>
                                Voltar para Pendente
                              </DropdownMenuItem>
                            </>
                          )}
                          {item.acquisition_status === "DONE" && (
                            <DropdownMenuItem onClick={() => onReopen(item)}>
                              Reabrir Aquisição
                            </DropdownMenuItem>
                          )}

                          <DropdownMenuSeparator />

                          {isDiscarded ? (
                            <DropdownMenuItem onClick={() => onInclude(item)}>
                              Reintegrar ao Escopo
                            </DropdownMenuItem>
                          ) : (
                            <DropdownMenuItem onClick={() => setDiscardingItem(item)}>
                              Descartar do Escopo
                            </DropdownMenuItem>
                          )}

                          {delivery !== "DELIVERED" ? (
                            <DropdownMenuItem onClick={() => onDeliver(item)}>
                              Marcar como Entregue
                            </DropdownMenuItem>
                          ) : (
                            <DropdownMenuItem onClick={() => onReturn(item)}>
                              Registrar Devolução
                            </DropdownMenuItem>
                          )}

                          <DropdownMenuSeparator />

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
                  </TableRow>
                );
              })
            )}
          </TableBody>
        </Table>
      </div>

      {/* Modal para Descartar Item com Justificativa Obrigatória (RF-15) */}
      <Dialog
        open={!!discardingItem}
        onOpenChange={(open) => {
          if (!open) {
            setDiscardingItem(null);
            setRejectionReason("");
          }
        }}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Descartar Item do Escopo</DialogTitle>
            <DialogDescription>
              Informe a justificativa técnica ou solicitação dos noivos para desconsiderar este item (obrigatório).
            </DialogDescription>
          </DialogHeader>
          <div className="flex flex-col gap-2 py-4">
            <label htmlFor="rejection-reason" className="text-sm font-medium">
              Motivo do Descarte *
            </label>
            <Textarea
              id="rejection-reason"
              placeholder="Ex: Fornecedor já inclui este material no pacote contratado."
              value={rejectionReason}
              onChange={(e) => setRejectionReason(e.target.value)}
              rows={3}
            />
          </div>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => {
                setDiscardingItem(null);
                setRejectionReason("");
              }}
            >
              Cancelar
            </Button>
            <Button
              variant="destructive"
              disabled={!rejectionReason.trim() || isDiscarding}
              onClick={handleConfirmDiscard}
            >
              Confirmar Descarte
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

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
    </div>
  );
});
