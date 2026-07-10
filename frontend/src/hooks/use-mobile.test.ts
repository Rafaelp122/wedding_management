import { renderHook } from "@/test-utils";
import { describe, it, expect, vi } from "vitest";
import { useIsMobile } from "./use-mobile";

describe("useIsMobile", () => {
  it("should return true when window width is less than MOBILE_BREAKPOINT (768px)", () => {
    const originalInnerWidth = window.innerWidth;
    const originalMatchMedia = window.matchMedia;

    window.innerWidth = 500;
    window.matchMedia = vi.fn().mockImplementation((query: string) => ({
      matches: true,
      media: query,
      onchange: null,
      addListener: vi.fn(),
      removeListener: vi.fn(),
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      dispatchEvent: vi.fn(),
    })) as unknown as (query: string) => MediaQueryList;

    try {
      const { result } = renderHook(() => useIsMobile());
      expect(result.current).toBe(true);
    } finally {
      window.innerWidth = originalInnerWidth;
      window.matchMedia = originalMatchMedia;
    }
  });

  it("should return false when window width is greater than or equal to MOBILE_BREAKPOINT (768px)", () => {
    const originalInnerWidth = window.innerWidth;
    const originalMatchMedia = window.matchMedia;

    window.innerWidth = 1024;
    window.matchMedia = vi.fn().mockImplementation((query: string) => ({
      matches: false,
      media: query,
      onchange: null,
      addListener: vi.fn(),
      removeListener: vi.fn(),
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      dispatchEvent: vi.fn(),
    })) as unknown as (query: string) => MediaQueryList;

    try {
      const { result } = renderHook(() => useIsMobile());
      expect(result.current).toBe(false);
    } finally {
      window.innerWidth = originalInnerWidth;
      window.matchMedia = originalMatchMedia;
    }
  });
});
