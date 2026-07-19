import { memo } from "react";
import type { ContractOut } from "@/api/generated/v1/models/contractOut";
import {
  useLogisticsItemsList,
  useLogisticsContractsRead,
  useLogisticsContractsList,
} from "@/api/generated/v1/endpoints/logistics/logistics";
import { ContractDetailDialogView } from "./ContractDetailDialogView";

interface ContractDetailDialogProps {
  contractUuid: string | null;
  weddingUuid: string;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onExpenseClick?: (expenseUuid: string | null) => void;
  onGenerateExpense?: (contract: ContractOut) => void;
  onSupplierClick?: (supplierUuid: string) => void;
  onCreateAddendum?: (parentUuid: string) => void;
}

export const ContractDetailDialog = memo(function ContractDetailDialog({
  contractUuid,
  weddingUuid,
  open,
  onOpenChange,
  onExpenseClick,
  onGenerateExpense,
  onSupplierClick,
  onCreateAddendum,
}: ContractDetailDialogProps) {
  const { data: contractResponse, isLoading: isContractLoading } =
    useLogisticsContractsRead(contractUuid ?? "", {
      query: { enabled: !!contractUuid && open, staleTime: 0 },
    });
  const contract = contractResponse?.data;

  const { data: itemsResponse, isLoading: isItemsLoading } =
    useLogisticsItemsList(
      { contract_id: contractUuid ?? "" },
      { query: { enabled: !!contractUuid && open } },
    );
  const items = itemsResponse?.data?.items ?? [];

  const { data: addendumsResponse } = useLogisticsContractsList(
    {
      wedding_id: weddingUuid,
      parent_id: contractUuid ?? "",
    },
    { query: { enabled: !!contractUuid && open } }
  );
  const addendums = addendumsResponse?.data?.items ?? [];

  return (
    <ContractDetailDialogView
      contractUuid={contractUuid}
      weddingUuid={weddingUuid}
      open={open}
      onOpenChange={onOpenChange}
      contract={contract}
      isContractLoading={isContractLoading}
      items={items}
      isItemsLoading={isItemsLoading}
      addendums={addendums}
      onExpenseClick={onExpenseClick}
      onGenerateExpense={onGenerateExpense}
      onSupplierClick={onSupplierClick}
      onCreateAddendum={onCreateAddendum}
    />
  );
});
