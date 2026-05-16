import { describe, expect, it } from "vitest";
import { renderHook, waitFor } from "@/test-utils";
import { useWeddingTimeline } from "@/features/scheduler/hooks/useTimeline";

describe("useWeddingTimeline", () => {
  const weddingUuid = "test-wedding-uuid";

  it("returns events after loading", async () => {
    const { result } = renderHook(() => useWeddingTimeline(weddingUuid));

    expect(result.current.isLoading).toBe(true);

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.events).toBeInstanceOf(Array);
    expect(result.current.error).toBeNull();
  });
});
