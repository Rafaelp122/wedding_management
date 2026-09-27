import { toast } from "sonner";
import { useQueryClient } from "@tanstack/react-query";

import type { ItemOut } from "@/api/generated/v1/models/itemOut";
import {
  useLogisticsItemsCreate,
  getLogisticsItemsListQueryKey,
} from "@/api/generated/v1/endpoints/logistics/logistics";
import { getApiErrorInfo } from "@/api/error-utils";
import {
  ContractItemsSectionView,
  type InlineItemData,
} from "./ContractItemsSectionView";

interface ContractItemsSectionProps {
  weddingUuid: string;
  contractUuid: string;
  items: ItemOut[];
  isLoading: boolean;
}

export function ContractItemsSection({
  weddingUuid,
  contractUuid,
  items,
  isLoading,
}: ContractItemsSectionProps) {
  const queryClient = useQueryClient();
  const { mutate: createItem, isPending: isCreatingItem } =
    useLogisticsItemsCreate();

  const handleAddItem = (data: InlineItemData, onDone: () => void) => {
    createItem(
      {
        data: {
          wedding: weddingUuid,
          contract: contractUuid,
          name: data.name,
          quantity: data.quantity,
          acquisition_status: data.acquisition_status,
        },
      },
      {
        onSuccess: () => {
          toast.success("Item adicionado!");
          onDone();
          queryClient.invalidateQueries({
            queryKey: getLogisticsItemsListQueryKey(),
          });
        },
        onError: (error) => {
          const { message } = getApiErrorInfo(error, "Erro ao criar item.");
          toast.error(message);
        },
      },
    );
  };

  return (
    <ContractItemsSectionView
      items={items}
      isLoading={isLoading}
      onAddItem={handleAddItem}
      isCreating={isCreatingItem}
    />
  );
}
