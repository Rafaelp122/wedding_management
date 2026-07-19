import { useCallback } from "react";
import { useQueryClient } from "@tanstack/react-query";
import type { AxiosResponse, InternalAxiosRequestConfig } from "axios";
import {
  useWeddingsRead,
  getWeddingsReadQueryKey,
  getWeddingsListQueryKey,
  getWeddingsOverviewReadQueryKey,
} from "@/api/generated/v1/endpoints/weddings/weddings";
import type { PagedWeddingOut } from "@/api/generated/v1/models/pagedWeddingOut";
import type { WeddingOut } from "@/api/generated/v1/models/weddingOut";

export function useWeddingDetail(uuid: string) {
  const queryClient = useQueryClient();

  const invalidateWeddingQueries = useCallback(() => {
    queryClient.invalidateQueries({ queryKey: getWeddingsReadQueryKey(uuid) });
    queryClient.invalidateQueries({ queryKey: getWeddingsListQueryKey() });
    queryClient.invalidateQueries({ queryKey: getWeddingsOverviewReadQueryKey(uuid) });
  }, [uuid, queryClient]);

  const queryResult = useWeddingsRead(uuid, {
    query: {
      enabled: !!uuid,
      placeholderData: () => {
        const cachedQueries = queryClient.getQueriesData<AxiosResponse<PagedWeddingOut>>({
          queryKey: ["/api/v1/weddings/"],
        });

        for (const [, queryData] of cachedQueries) {
          const weddingItem = queryData?.data?.items?.find(
            (item: WeddingOut) => item.uuid === uuid
          );
          if (weddingItem) {
            return {
              data: weddingItem,
              status: 200,
              statusText: "OK",
              headers: {},
              config: {
                headers: {} as unknown as InternalAxiosRequestConfig["headers"],
                method: "get",
                url: `/api/v1/weddings/${uuid}/`,
              } as InternalAxiosRequestConfig,
            };
          }
        }
        return undefined;
      },
    },
  });

  return {
    ...queryResult,
    invalidateWeddingQueries,
  };
}
