import "@testing-library/jest-dom/vitest";
import { cleanup } from "@testing-library/react";
import { afterAll, afterEach, beforeAll, vi } from "vitest";

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const globalAny = globalThis as any;

if (!globalAny.__SONNER_MOCK__) {
  globalAny.__SONNER_MOCK__ = {
    success: vi.fn(),
    error: vi.fn(),
    warning: vi.fn(),
    info: vi.fn(),
    loading: vi.fn(),
    dismiss: vi.fn(),
    custom: vi.fn(),
  };
}

if (!globalAny.__SENTRY_MOCK__) {
  globalAny.__SENTRY_MOCK__ = {
    setContext: vi.fn(),
    captureException: vi.fn(),
  };
}

vi.mock("sonner", async (importOriginal) => {
  const actual = await importOriginal<typeof import("sonner")>();
  return {
    ...actual,
    toast: globalAny.__SONNER_MOCK__,
  };
});

vi.mock("@sentry/react", () => globalAny.__SENTRY_MOCK__);

import { server } from "@/mocks/server";
import { useAuthStore } from "@/stores/authStore";

beforeAll(() => {
  server.listen({ onUnhandledRequest: "warn" });

  if (!globalAny.__HAPPY_DOM_SUBMIT_BUG_FIXED__) {
    globalAny.__HAPPY_DOM_SUBMIT_BUG_FIXED__ = true;

    // Workaround for Happy DOM bug where clicking a submit button with children inside a form
    // fails to submit the form due to event propagation issues.
    window.addEventListener(
      "submit",
      (e) => {
        const form = e.target as HTMLFormElement & { _hasSubmittedInTick?: boolean };
        if (form && form.tagName === "FORM") {
          form._hasSubmittedInTick = true;
          setTimeout(() => {
            form._hasSubmittedInTick = false;
          }, 0);
        }
      },
      { capture: true }
    );

    const originalDispatchEvent = HTMLElement.prototype.dispatchEvent;
    HTMLElement.prototype.dispatchEvent = function (event) {
      const result = originalDispatchEvent.call(this, event);
      if (event.type === "click") {
        const button = this.closest("button");
        if (
          button &&
          button.type === "submit" &&
          !button.disabled
        ) {
          const form = button.closest("form") as HTMLFormElement & { _hasSubmittedInTick?: boolean };
          if (form && !form._hasSubmittedInTick) {
            form._hasSubmittedInTick = true;
            setTimeout(() => {
              form._hasSubmittedInTick = false;
            }, 0);
            form.dispatchEvent(
              new window.Event("submit", {
                bubbles: true,
                cancelable: true,
              })
            );
          }
        }
      }
      return result;
    };
  }

  Object.defineProperty(window, "matchMedia", {
    writable: true,
    value: vi.fn().mockImplementation((query: string) => ({
      matches: false,
      media: query,
      onchange: null,
      addListener: vi.fn(),
      removeListener: vi.fn(),
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      dispatchEvent: vi.fn(),
    })),
  });
  globalThis.ResizeObserver = vi.fn(function ResizeObserver() {
    return {
      observe: vi.fn(),
      unobserve: vi.fn(),
      disconnect: vi.fn(),
    };
  });
});

afterEach(() => {
  cleanup();
  server.resetHandlers();
  vi.clearAllMocks();
  document.body.removeAttribute("data-scroll-locked");
  document.body.style.pointerEvents = "";
  document.documentElement.style.pointerEvents = "";
  useAuthStore.getState().logout();
});

afterAll(() => server.close());
