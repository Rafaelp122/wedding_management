import { describe, expect, it, vi } from "vitest";
import { act, renderHook } from "@/test-utils";
import { useDebounce } from "@/hooks/use-debounce";

describe("useDebounce", () => {
  it("should return the initial value immediately", () => {
    const { result } = renderHook(() => useDebounce("hello", 300));
    expect(result.current).toBe("hello");
  });

  it("should delay updating the value", () => {
    vi.useFakeTimers();
    let value = "hello";
    const { result, rerender } = renderHook(() => useDebounce(value, 300));

    expect(result.current).toBe("hello");

    value = "world";
    rerender();

    // Value should not be updated immediately
    expect(result.current).toBe("hello");

    // Advance time by 299ms
    act(() => {
      vi.advanceTimersByTime(299);
    });
    expect(result.current).toBe("hello");

    // Advance remaining 1ms
    act(() => {
      vi.advanceTimersByTime(1);
    });
    expect(result.current).toBe("world");

    vi.useRealTimers();
  });
});
