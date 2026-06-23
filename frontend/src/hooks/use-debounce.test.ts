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

  it("should reset the timer when the value changes before the delay expires", () => {
    vi.useFakeTimers();
    let value = "hello";
    const { result, rerender } = renderHook(() => useDebounce(value, 300));

    expect(result.current).toBe("hello");

    value = "world";
    rerender();

    // Advance time by 150ms
    act(() => {
      vi.advanceTimersByTime(150);
    });
    expect(result.current).toBe("hello");

    // Change value again, which should reset the timer
    value = "reset";
    rerender();

    // Advance time by another 200ms (total 350ms elapsed, but only 200ms since second change)
    act(() => {
      vi.advanceTimersByTime(200);
    });
    expect(result.current).toBe("hello");

    // Advance remaining 100ms
    act(() => {
      vi.advanceTimersByTime(100);
    });
    expect(result.current).toBe("reset");

    vi.useRealTimers();
  });
});
