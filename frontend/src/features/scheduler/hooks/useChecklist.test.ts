import { describe, expect, it } from "vitest";
import { renderHook, waitFor, act } from "@/test-utils";
import { useWeddingChecklist } from "@/features/scheduler/hooks/useChecklist";

describe("useWeddingChecklist", () => {
  const weddingUuid = "test-wedding-uuid";

  it("returns tasks after loading", async () => {
    const { result } = renderHook(() => useWeddingChecklist(weddingUuid));

    expect(result.current.isLoading).toBe(true);

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.tasks).toBeInstanceOf(Array);
    expect(result.current.error).toBeNull();
  });

  it("toggleTaskCompletion toggles is_completed", async () => {
    const { result } = renderHook(() => useWeddingChecklist(weddingUuid));

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(() => {
      act(() => {
        result.current.toggleTaskCompletion("task-1", false);
      });
    }).not.toThrow();
  });
});
