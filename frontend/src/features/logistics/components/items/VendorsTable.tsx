import { memo } from "react";

import type { ContractOut } from "@/api/generated/v1/models/contractOut";
import {
  useContractsDelete,
} from "@/api/generated/v1/endpoints/contracts/contracts";
import { createMutationCallbacks } from "@/hooks/use-mutation-toast";
import { WeddingVendorsTableView } from "./VendorsTableView";

interface WeddingVendorsTableProps {
  contracts: ContractOut[];
  isAddendum?: (contract: ContractOut) => boolean;
  onDetail?: (uuid: string) => void;
  onEdit?: (contract: ContractOut) => void;
  onGenerateExpense?: (contract: ContractOut) => void;
  onRefresh?: () => void;
}

export const WeddingVendorsTable = memo(function WeddingVendorsTable({
  contracts,
  isAddendum,
  onDetail,
  onEdit,
  onGenerateExpense,
  onRefresh,
}: WeddingVendorsTableProps) {
  const { mutate: deleteContract, isPending: isDeleting } =
    useContractsDelete();

  const handleConfirmDelete = (contract: ContractOut, onDone: () => void) => {
    deleteContract(
      { uuid: contract.uuid },
      createMutationCallbacks({
        successMsg: "Contrato deletado com sucesso!",
        fallbackErrorMsg: "Erro ao deletar contrato.",
        onSuccess: () => {
          onDone();
          onRefresh?.();
        },
      }),
    );
  };

  return (
    <WeddingVendorsTableView
      contracts={contracts}
      isAddendum={isAddendum}
      onDetail={onDetail}
      onEdit={onEdit}
      onGenerateExpense={onGenerateExpense}
      onRefresh={onRefresh}
      onConfirmDelete={handleConfirmDelete}
      isDeleting={isDeleting}
    />
  );
});
