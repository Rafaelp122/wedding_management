import { describe, expect, it } from "vitest";
import { renderHook, waitFor } from "@/test-utils";
import { useWeddingVendorsItems } from "@/features/logistics/hooks/useVendorsItems";

describe("useWeddingVendorsItems", () => {
  const weddingUuid = "test-wedding-uuid";

  it("returns contracts and items after loading", async () => {
    const { result } = renderHook(() => useWeddingVendorsItems(weddingUuid));

    expect(result.current.isLoading).toBe(true);

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.contracts).toBeInstanceOf(Array);
    expect(result.current.items).toBeInstanceOf(Array);
    expect(result.current.error).toBeNull();
  });
});
