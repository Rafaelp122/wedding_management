import { memo, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

import type { ContractOut } from "@/api/generated/v1/models/contractOut";
import type { ContractAddendumOut } from "@/api/generated/v1/models/contractAddendumOut";
import {
  useContractsDetailsRead,
  useContractsStatusTransition,
  getContractsListQueryKey,
  getContractsReadQueryKey,
  getContractsDetailsReadQueryKey,
  getContractsAddendumsListQueryKey,
} from "@/api/generated/v1/endpoints/contracts/contracts";
import { getApiErrorInfo } from "@/api/error-utils";
import { ContractDetailDialogView } from "./ContractDetailDialogView";
import { CancelContractDialog } from "./CancelContractDialog";
import { SignContractDialog } from "./SignContractDialog";
import { CreateAddendumDialog } from "./CreateAddendumDialog";
import { SignAddendumDialog } from "./SignAddendumDialog";

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
  const [createAddendumOpen, setCreateAddendumOpen] = useState(false);
  const [signAddendumOpen, setSignAddendumOpen] = useState(false);
  const [selectedAddendum, setSelectedAddendum] = useState<ContractAddendumOut | null>(null);

  const { data: detailsResponse, isLoading } =
    useContractsDetailsRead(contractUuid ?? "", {
      query: { enabled: !!contractUuid && open, staleTime: 0 },
    });
  const contract = detailsResponse?.data?.contract;
  const items = detailsResponse?.data?.items ?? [];
  const addendums = detailsResponse?.data?.addendums ?? [];

  const invalidateContractQueries = () => {
    queryClient.invalidateQueries({
      queryKey: getContractsListQueryKey(),
    });
    if (contractUuid) {
      queryClient.invalidateQueries({
        queryKey: getContractsDetailsReadQueryKey(contractUuid),
      });
      queryClient.invalidateQueries({
        queryKey: getContractsReadQueryKey(contractUuid),
      });
      queryClient.invalidateQueries({
        queryKey: getContractsAddendumsListQueryKey(contractUuid),
      });
    }
  };

  const {
    mutate: transitionStatus,
    isPending: isTransitionPending,
  } = useContractsStatusTransition();

  const handleSendToPending = () => {
    if (!contract) return;
    transitionStatus(
      {
        uuid: contract.uuid,
        data: {
          status: "PENDING",
        },
      },
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
    transitionStatus(
      {
        uuid: contract.uuid,
        data: {
          status: "DRAFT",
        },
      },
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

  const handleCreateAddendum = (parentUuid: string) => {
    if (onCreateAddendum) {
      onCreateAddendum(parentUuid);
    } else {
      setCreateAddendumOpen(true);
    }
  };

  const handleSignAddendum = (addendum: ContractAddendumOut) => {
    setSelectedAddendum(addendum);
    setSignAddendumOpen(true);
  };

  return (
    <>
      <ContractDetailDialogView
        contractUuid={contractUuid}
        weddingUuid={weddingUuid}
        open={open}
        onOpenChange={onOpenChange}
        contract={contract}
        isContractLoading={isLoading}
        items={items}
        isItemsLoading={isLoading}
        addendums={addendums}
        onExpenseClick={onExpenseClick}
        onGenerateExpense={onGenerateExpense}
        onSupplierClick={onSupplierClick}
        onCreateAddendum={handleCreateAddendum}
        onSignAddendum={handleSignAddendum}
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

      {contractUuid && (
        <>
          <CreateAddendumDialog
            contractUuid={contractUuid}
            open={createAddendumOpen}
            onOpenChange={setCreateAddendumOpen}
            onSuccess={invalidateContractQueries}
          />

          <SignAddendumDialog
            contractUuid={contractUuid}
            addendum={selectedAddendum}
            open={signAddendumOpen}
            onOpenChange={setSignAddendumOpen}
            onSuccess={invalidateContractQueries}
          />
        </>
      )}
    </>
  );
});
