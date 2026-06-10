import { describe, expect, it } from "vitest";
import { renderHook } from "@testing-library/react";
import { useDocumentTitle } from "@/hooks/useDocumentTitle";

describe("useDocumentTitle", () => {
  it("sets the document title with the given title", () => {
    const { unmount } = renderHook(() => useDocumentTitle("Entrar"));
    expect(document.title).toBe("Entrar | Sim, Aceito!");
    unmount();
  });

  it("sets base title when no title is provided", () => {
    const { unmount } = renderHook(() => useDocumentTitle());
    expect(document.title).toBe("Sim, Aceito!");
    unmount();
  });

  it("restores previous document title on unmount", () => {
    document.title = "Before";
    const { unmount } = renderHook(() => useDocumentTitle("Test"));
    expect(document.title).toBe("Test | Sim, Aceito!");
    unmount();
    expect(document.title).toBe("Before");
  });
});
