import { useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import type { ItemOut } from "@/api/generated/v1/models/itemOut";
import { getLogisticsItemsListQueryKey } from "@/api/generated/v1/endpoints/logistics/logistics";

export function useVendorsItemsOrchestrator() {
  const queryClient = useQueryClient();

  const [detailContractUuid, setDetailContractUuid] = useState<string | null>(null);
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
