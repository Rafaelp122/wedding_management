
import { describe, expect, it } from "vitest";
import { QueryClient } from "@tanstack/react-query";
import { renderHook, server } from "@/test-utils";
import { useWeddingDetail } from "@/features/weddings/hooks/useWeddingDetail";
import { http, HttpResponse } from "msw";
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

    server.use(
      http.get("*/api/v1/weddings/test-wedding-uuid-123/", () => {
        return HttpResponse.json(mockWedding);
      })
    );

    const queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
      },
    });


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


    const { result } = renderHook(() => useWeddingDetail(uuid), { queryClient });


    expect(result.current.data?.data).toBeDefined();
    expect(result.current.data?.data.groom_name).toBe("Noivo Teste");
    expect(result.current.data?.data.bride_name).toBe("Noiva Teste");
  });

  it("returns undefined if no cached wedding matches the uuid", async () => {
    const uuid = "non-existent-uuid";

    server.use(
      http.get("*/api/v1/weddings/non-existent-uuid/", () => {
        return new HttpResponse(null, { status: 404 });
      })
    );

    const queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
      },
    });


    const { result } = renderHook(() => useWeddingDetail(uuid), { queryClient });


    expect(result.current.data).toBeUndefined();
  });

  it("invalidates wedding queries on demand", () => {
    const { result } = renderHook(() => useWeddingDetail("w-1"));

    expect(() => result.current.invalidateWeddingQueries()).not.toThrow();
  });
});
