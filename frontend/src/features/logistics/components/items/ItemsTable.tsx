import { memo } from "react";

import type { ItemOut } from "@/api/generated/v1/models/itemOut";
import {
  useLogisticsItemsDelete,
  useLogisticsItemsStart,
  useLogisticsItemsComplete,
  useLogisticsItemsReopen,
  useLogisticsItemsRevertToPending,
  useLogisticsItemsDiscard,
  useLogisticsItemsInclude,
  useLogisticsItemsDeliver,
  useLogisticsItemsReturn,
} from "@/api/generated/v1/endpoints/logistics/logistics";
import { createMutationCallbacks } from "@/hooks/use-mutation-toast";
import { WeddingItemsTableView } from "./ItemsTableView";

interface WeddingItemsTableProps {
  items: ItemOut[];
  onEdit?: (item: ItemOut) => void;
  onRefresh?: () => void;
}

export const WeddingItemsTable = memo(function WeddingItemsTable({
  items,
  onEdit,
  onRefresh,
}: WeddingItemsTableProps) {
  const { mutate: deleteItem, isPending: isDeleting } = useLogisticsItemsDelete();
  const { mutate: startItem } = useLogisticsItemsStart();
  const { mutate: completeItem } = useLogisticsItemsComplete();
  const { mutate: reopenItem } = useLogisticsItemsReopen();
  const { mutate: revertToPendingItem } = useLogisticsItemsRevertToPending();
  const { mutate: discardItem, isPending: isDiscarding } = useLogisticsItemsDiscard();
  const { mutate: includeItem } = useLogisticsItemsInclude();
  const { mutate: deliverItem } = useLogisticsItemsDeliver();
  const { mutate: returnItem } = useLogisticsItemsReturn();

  const handleDelete = (item: ItemOut, onDone: () => void) => {
    deleteItem(
      { uuid: item.uuid },
      createMutationCallbacks({
        successMsg: "Item deletado com sucesso!",
        fallbackErrorMsg: "Erro ao deletar item.",
        onSuccess: () => {
          onDone();
          onRefresh?.();
        },
      }),
    );
  };

  const handleStart = (item: ItemOut) => {
    startItem(
      { uuid: item.uuid },
      createMutationCallbacks({
        successMsg: "Aquisição do item iniciada!",
        fallbackErrorMsg: "Erro ao iniciar aquisição.",
        onSuccess: () => onRefresh?.(),
      }),
    );
  };

  const handleComplete = (item: ItemOut) => {
    completeItem(
      { uuid: item.uuid },
      createMutationCallbacks({
        successMsg: "Item concluído com sucesso!",
        fallbackErrorMsg: "Erro ao concluir item.",
        onSuccess: () => onRefresh?.(),
      }),
    );
  };

  const handleReopen = (item: ItemOut) => {
    reopenItem(
      { uuid: item.uuid },
      createMutationCallbacks({
        successMsg: "Item reaberto com sucesso!",
        fallbackErrorMsg: "Erro ao reabrir item.",
        onSuccess: () => onRefresh?.(),
      }),
    );
  };

  const handleRevertToPending = (item: ItemOut) => {
    revertToPendingItem(
      { uuid: item.uuid },
      createMutationCallbacks({
        successMsg: "Item retornado para pendente!",
        fallbackErrorMsg: "Erro ao retornar item para pendente.",
        onSuccess: () => onRefresh?.(),
      }),
    );
  };

  const handleConfirmDiscard = (item: ItemOut, reason: string, onDone: () => void) => {
    discardItem(
      {
        uuid: item.uuid,
        data: { rejection_reason: reason },
      },
      createMutationCallbacks({
        successMsg: "Item descartado do escopo com sucesso!",
        fallbackErrorMsg: "Erro ao descartar item.",
        onSuccess: () => {
          onDone();
          onRefresh?.();
        },
      }),
    );
  };

  const handleInclude = (item: ItemOut) => {
    includeItem(
      { uuid: item.uuid },
      createMutationCallbacks({
        successMsg: "Item reintegrado ao escopo com sucesso!",
        fallbackErrorMsg: "Erro ao reintegrar item.",
        onSuccess: () => onRefresh?.(),
      }),
    );
  };

  const handleDeliver = (item: ItemOut) => {
    deliverItem(
      { uuid: item.uuid },
      createMutationCallbacks({
        successMsg: "Item marcado como entregue!",
        fallbackErrorMsg: "Erro ao marcar entrega.",
        onSuccess: () => onRefresh?.(),
      }),
    );
  };

  const handleReturn = (item: ItemOut) => {
    returnItem(
      { uuid: item.uuid },
      createMutationCallbacks({
        successMsg: "Item marcado como devolvido!",
        fallbackErrorMsg: "Erro ao registrar devolução.",
        onSuccess: () => onRefresh?.(),
      }),
    );
  };

  return (
    <WeddingItemsTableView
      items={items}
      onEdit={onEdit}
      onDelete={handleDelete}
      isDeleting={isDeleting}
      onStart={handleStart}
      onComplete={handleComplete}
      onReopen={handleReopen}
      onRevertToPending={handleRevertToPending}
      onConfirmDiscard={handleConfirmDiscard}
      isDiscarding={isDiscarding}
      onInclude={handleInclude}
      onDeliver={handleDeliver}
      onReturn={handleReturn}
    />
  );
});
