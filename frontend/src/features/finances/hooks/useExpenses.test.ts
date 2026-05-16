import { describe, expect, it } from "vitest";
import { renderHook, waitFor } from "@/test-utils";
import { useWeddingExpenses } from "@/features/finances/hooks/useExpenses";

describe("useWeddingExpenses", () => {
  const weddingUuid = "test-wedding-uuid";

  it("returns expenses after loading", async () => {
    const { result } = renderHook(() => useWeddingExpenses(weddingUuid));

    expect(result.current.isLoading).toBe(true);

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.expenses).toBeInstanceOf(Array);
    expect(result.current.error).toBeNull();
  });
});
