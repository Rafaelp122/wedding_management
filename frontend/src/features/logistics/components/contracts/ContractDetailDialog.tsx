import { memo, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

import type { ContractOut } from "@/api/generated/v1/models/contractOut";
import {
  useLogisticsItemsList,
  useLogisticsContractsRead,
  useLogisticsContractsList,
  useLogisticsContractsSendToPending,
  useLogisticsContractsRevertToDraft,
  getLogisticsContractsListQueryKey,
  getLogisticsContractsReadQueryKey,
} from "@/api/generated/v1/endpoints/logistics/logistics";
import { getApiErrorInfo } from "@/api/error-utils";
import { ContractDetailDialogView } from "./ContractDetailDialogView";
import { CancelContractDialog } from "./CancelContractDialog";
import { SignContractDialog } from "./SignContractDialog";

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
  const queryClient = useQueryClient();
  const [cancelOpen, setCancelOpen] = useState(false);
  const [signOpen, setSignOpen] = useState(false);

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
    { query: { enabled: !!contractUuid && open } },
  );
  const addendums = addendumsResponse?.data?.items ?? [];

  const invalidateContractQueries = () => {
    queryClient.invalidateQueries({
      queryKey: getLogisticsContractsListQueryKey(),
    });
    if (contractUuid) {
      queryClient.invalidateQueries({
        queryKey: getLogisticsContractsReadQueryKey(contractUuid),
      });
    }
  };

  const {
    mutate: sendToPending,
    isPending: isPendingSend,
  } = useLogisticsContractsSendToPending();

  const {
    mutate: revertToDraft,
    isPending: isPendingRevert,
  } = useLogisticsContractsRevertToDraft();

  const handleSendToPending = () => {
    if (!contract) return;
    sendToPending(
      { uuid: contract.uuid },
      {
        onSuccess: () => {
          toast.success("Contrato enviado para assinatura!");
          invalidateContractQueries();
        },
        onError: (error) => {
          const { message } = getApiErrorInfo(
            error,
            "Erro ao enviar contrato para assinatura.",
          );
          toast.error(message);
        },
      },
    );
  };

  const handleRevertToDraft = () => {
    if (!contract) return;
    revertToDraft(
      { uuid: contract.uuid },
      {
        onSuccess: () => {
          toast.success("Contrato retornado para rascunho!");
          invalidateContractQueries();
        },
        onError: (error) => {
          const { message } = getApiErrorInfo(
            error,
            "Erro ao reverter contrato para rascunho.",
          );
          toast.error(message);
        },
      },
    );
  };

  const isTransitionPending = isPendingSend || isPendingRevert;

  return (
    <>
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
        onSendToPending={handleSendToPending}
        onSign={() => setSignOpen(true)}
        onCancel={() => setCancelOpen(true)}
        onRevertToDraft={handleRevertToDraft}
        isTransitionPending={isTransitionPending}
      />

      <CancelContractDialog
        contract={contract ?? null}
        open={cancelOpen}
        onOpenChange={setCancelOpen}
        onSuccess={invalidateContractQueries}
      />

      <SignContractDialog
        contract={contract ?? null}
        open={signOpen}
        onOpenChange={setSignOpen}
        onSuccess={invalidateContractQueries}
      />
    </>
  );
});
