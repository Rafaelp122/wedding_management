import React from "react";
import { describe, expect, it } from "vitest";
import { renderHook } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useWeddingDetail } from "@/features/weddings/hooks/useWeddingDetail";
import type { AxiosResponse } from "axios";
import type { PagedWeddingOut } from "@/api/generated/v1/models/pagedWeddingOut";
import type { WeddingOut } from "@/api/generated/v1/models/weddingOut";

describe("useWeddingDetail", () => {
  it("uses cached weddings list data as placeholderData", async () => {
    const uuid = "test-wedding-uuid-123";
    const mockWedding = {
      uuid,
      groom_name: "Noivo Teste",
      bride_name: "Noiva Teste",
      wedding_date: "2026-12-25",
      status: "PLANNING" as const,
    };

    const queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
      },
    });

    const wrapper = ({ children }: { children: React.ReactNode }) => (
      <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
    );

    // Popula o cache da listagem de casamentos
    queryClient.setQueryData<AxiosResponse<PagedWeddingOut>>(
      ["/api/v1/weddings/"],
      {
        data: {
          items: [mockWedding as unknown as WeddingOut],
          count: 1,
        },
        status: 200,
        statusText: "OK",
        headers: {},
        config: {} as unknown as AxiosResponse["config"],
      }
    );

    // Executa o hook useWeddingDetail
    const { result } = renderHook(() => useWeddingDetail(uuid), { wrapper });

    // O status do data deve ser imediatamente populado pelo cache antes de terminar a query de leitura real
    expect(result.current.data?.data).toBeDefined();
    expect(result.current.data?.data.groom_name).toBe("Noivo Teste");
    expect(result.current.data?.data.bride_name).toBe("Noiva Teste");
  });
});
