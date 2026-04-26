import {
  useLogisticsContractsList,
  useLogisticsItemsList,
} from "@/api/generated/v1/endpoints/logistics/logistics";

export function useWeddingVendorsItems(weddingUuid: string) {
  const {
    data: contractsData,
    isLoading: isLoadingContracts,
    error: contractsError,
  } = useLogisticsContractsList({ wedding_id: weddingUuid });

  const {
    data: itemsData,
    isLoading: isLoadingItems,
    error: itemsError,
  } = useLogisticsItemsList({ wedding_id: weddingUuid });

  const contracts = contractsData?.data?.items ?? [];
  const items = itemsData?.data?.items ?? [];

  const isLoading = isLoadingContracts || isLoadingItems;
  const error = contractsError || itemsError;

  return {
    contracts,
    items,
    isLoading,
    error,
  };
}
