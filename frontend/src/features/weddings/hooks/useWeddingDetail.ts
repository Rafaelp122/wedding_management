import { useQueryClient } from "@tanstack/react-query";
import type { AxiosResponse, InternalAxiosRequestConfig } from "axios";
import { useWeddingsRead } from "@/api/generated/v1/endpoints/weddings/weddings";
import type { PagedWeddingOut } from "@/api/generated/v1/models/pagedWeddingOut";
import type { WeddingOut } from "@/api/generated/v1/models/weddingOut";

export function useWeddingDetail(uuid: string) {
  const queryClient = useQueryClient();

  return useWeddingsRead(uuid, {
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
            // Retorna um objeto AxiosResponse mockado completo para evitar quebras em interceptores
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
}
