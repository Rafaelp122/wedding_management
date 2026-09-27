import { useEffect, useRef, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import type { ItemOut } from "@/api/generated/v1/models/itemOut";
import { getLogisticsItemsListQueryKey } from "@/api/generated/v1/endpoints/logistics/logistics";

/**
 * Hook orquestrador para gerenciar estados de exibição e fluxo de contratos, aditivos e itens de fornecedores.
 *
 * Recebe o UUID inicial via props (lido da rota pelo container) em vez de
 * acessar `useSearchParams` diretamente.
 */
export function useVendorsItemsOrchestrator(
  options: { initialContractUuid?: string | null } = {},
) {
  const queryClient = useQueryClient();
  const contractIdParam = options.initialContractUuid ?? null;
  const openedContractRef = useRef<string | null>(null);

  const [detailContractUuid, setDetailContractUuid] = useState<string | null>(contractIdParam);

  useEffect(() => {
    if (contractIdParam && openedContractRef.current !== contractIdParam) {
      setDetailContractUuid(contractIdParam);
      openedContractRef.current = contractIdParam;
    }
  }, [contractIdParam]);
  const [uploadOpen, setUploadOpen] = useState(false);
  const [prefilledParentUuid, setPrefilledParentUuid] = useState<string | null>(null);
  const [createItemOpen, setCreateItemOpen] = useState(false);
  const [editItem, setEditItem] = useState<ItemOut | null>(null);

  const refreshItems = () => {
    queryClient.invalidateQueries({ queryKey: getLogisticsItemsListQueryKey() });
  };

  const handleCreateAddendum = (parentUuid: string) => {
    setPrefilledParentUuid(parentUuid);
    setUploadOpen(true);
    setDetailContractUuid(null);
  };

  const handleNewContractClick = () => {
    setPrefilledParentUuid(null);
    setUploadOpen(true);
  };

  return {
    detailContractUuid,
    setDetailContractUuid,
    uploadOpen,
    setUploadOpen,
    prefilledParentUuid,
    setPrefilledParentUuid,
    createItemOpen,
    setCreateItemOpen,
    editItem,
    setEditItem,
    refreshItems,
    handleCreateAddendum,
    handleNewContractClick,
  };
}
