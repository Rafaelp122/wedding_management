/**
 * TEST SETUP GLOBAL - WMS Frontend
 *
 * Regras Críticas de Mock e Interceptação de Rede (Vitest isolate: false):
 *
 * 1. NUNCA use `vi.mock("@/api/generated/...", () => ({...}))` dentro de arquivos de teste individuais.
 *    Sob a execução compartilhada de módulos (isolate: false), isso causará colisões e vazamento de estado
 *    entre as execuções de testes concorrentes.
 *
 * 2. PREFIRA SEMPRE O MSW (Mock Service Worker) para testes integrados e de fluxos visuais.
 *    Use o interceptador MSW (`server.use(http.get("/api/...", () => ...))`) para mockar endpoints de API.
 *    Dessa forma, os testes rodam de forma síncrona/assíncrona confiável, testando a integração real com a
 *    camada gerada do Orval e TanStack Query sem poluir o escopo global do Vitest.
 *
 * 3. MOCKS GLOBAIS DE HOOKS (Se estritamente inevitáveis):
 *    Todos os mocks de hooks Orval globais permitidos devem ser registrados de forma centralizada e controlada
 */

import "@testing-library/jest-dom/vitest";
import { cleanup } from "@testing-library/react";
import { afterAll, afterEach, beforeAll, vi } from "vitest";
import React from "react";

vi.mock("recharts", () => ({
  ResponsiveContainer: ({
    children,
    width,
    height,
  }: {
    children: React.ReactNode;
    width?: string | number;
    height?: string | number;
  }) => React.createElement("div", { "data-testid": "recharts-container", style: { width, height } }, children),
  BarChart: ({
    children,
    data,
  }: {
    children: React.ReactNode;
    data: unknown[];
  }) => React.createElement("div", { "data-testid": "bar-chart", "data-items": data.length }, children),
  Bar: ({ dataKey, name }: { dataKey: string; name?: string }) =>
    React.createElement("div", { "data-testid": `bar-${dataKey}` }, name),
  CartesianGrid: () => React.createElement("div", { "data-testid": "cartesian-grid" }),
  XAxis: ({ dataKey }: { dataKey: string }) =>
    React.createElement("div", { "data-testid": "x-axis", "data-datakey": dataKey }),
  YAxis: () => React.createElement("div", { "data-testid": "y-axis" }),
  Tooltip: () => React.createElement("div", { "data-testid": "tooltip" }),
  Legend: () => React.createElement("div", { "data-testid": "legend" }),
}));
vi.mock("@/features/finances/components/FinancesView", () => ({
  WeddingFinancesView: () => React.createElement("div", { "data-testid": "mock-finances-tab" }),
}));

vi.mock("@/features/logistics/components/VendorsItemsView", () => ({
  WeddingVendorsItemsTab: () => React.createElement("div", { "data-testid": "mock-logistics-tab" }),
}));

vi.mock("@/features/scheduler/components/events/TimelineView", () => ({
  WeddingTimelineTab: () => React.createElement("div", { "data-testid": "mock-timeline-tab" }),
}));

vi.mock("@/features/scheduler/components/tasks/ChecklistView", () => ({
  WeddingChecklistTab: () => React.createElement("div", { "data-testid": "mock-checklist-tab" }),
}));

const dropdownListeners = new Set<() => void>();
let hasAnyTriggerBeenClicked = false;

const setHasAnyTriggerBeenClicked = (val: boolean) => {
  hasAnyTriggerBeenClicked = val;
  dropdownListeners.forEach((listener) => listener());
};

const useHasAnyTriggerBeenClicked = () => {
  const [state, setState] = React.useState(hasAnyTriggerBeenClicked);
  React.useEffect(() => {
    const handler = () => setState(hasAnyTriggerBeenClicked);
    dropdownListeners.add(handler);
    return () => {
      dropdownListeners.delete(handler);
    };
  }, []);
  return state;
};

const DropdownMenuContext = React.createContext<{
  open: boolean;
  setOpen: (open: boolean) => void;
}>({
  open: false,
  setOpen: () => {},
});

vi.mock("@/components/ui/dropdown-menu", () => {
  return {
    DropdownMenu: ({
      children,
      open,
      onOpenChange,
    }: {
      children: React.ReactNode;
      open?: boolean;
      onOpenChange?: (open: boolean) => void;
    }) => {
      const [localOpen, setLocalOpen] = React.useState(false);
      const isOpen = open !== undefined ? open : localOpen;
      const setOpen = React.useCallback(
        (val: boolean) => {
          setLocalOpen(val);
          if (onOpenChange) onOpenChange(val);
        },
        [onOpenChange]
      );
      return React.createElement(
        DropdownMenuContext.Provider,
        { value: { open: isOpen, setOpen } },
        children
      );
    },
    DropdownMenuTrigger: ({
      children,
      asChild,
      ...props
    }: {
      children: React.ReactNode;
      asChild?: boolean;
    }) => {
      const { setOpen } = React.useContext(DropdownMenuContext);
      const handleClick = React.useCallback(
        (e: React.MouseEvent) => {
          setHasAnyTriggerBeenClicked(true);
          e.stopPropagation();
          setOpen(true);
        },
        [setOpen]
      );

      if (asChild && React.isValidElement(children)) {
        const childElement = children as React.ReactElement<{ onClick?: (e: React.MouseEvent) => void }>;
        return React.cloneElement(childElement, {
          onClick: (e: React.MouseEvent) => {
            if (childElement.props.onClick) childElement.props.onClick(e);
            handleClick(e);
          },
          ...props,
        });
      }

      return React.createElement(
        "button",
        { onClick: handleClick, ...props },
        children
      );
    },
    DropdownMenuContent: ({
      children,
      ...props
    }: {
      children: React.ReactNode;
    }) => {
      const { open } = React.useContext(DropdownMenuContext);
      const clicked = useHasAnyTriggerBeenClicked();
      if (clicked && !open) return null;
      return React.createElement("div", props, children);
    },
    DropdownMenuItem: ({
      children,
      onClick,
      className,
      ...props
    }: {
      children: React.ReactNode;
      onClick?: () => void;
      className?: string;
    }) => {
      const { setOpen } = React.useContext(DropdownMenuContext);
      const handleClick = React.useCallback(
        () => {
          if (onClick) onClick();
          setOpen(false);
        },
        [onClick, setOpen]
      );
      return React.createElement(
        "div",
        { role: "menuitem", className, onClick: handleClick, ...props },
        children
      );
    },
    DropdownMenuLabel: ({ children }: { children: React.ReactNode }) =>
      React.createElement("div", null, children),
    DropdownMenuSeparator: () => React.createElement("hr"),
    DropdownMenuGroup: ({ children }: { children: React.ReactNode }) =>
      React.createElement(React.Fragment, null, children),
    DropdownMenuSub: ({ children }: { children: React.ReactNode }) =>
      React.createElement(React.Fragment, null, children),
    DropdownMenuSubTrigger: ({ children }: { children: React.ReactNode }) =>
      React.createElement("button", null, children),
    DropdownMenuSubContent: ({ children }: { children: React.ReactNode }) =>
      React.createElement("div", null, children),
  };
});

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
vi.mock("react-router-dom", async (importOriginal) => {
  const actual = await importOriginal<typeof import("react-router-dom")>();
  return {
    ...actual,
    useRouteError: vi.fn(),
  };
});

import { server } from "@/mocks/server";
import { useAuthStore } from "@/stores/authStore";

beforeAll(() => {
  server.listen({ onUnhandledRequest: "warn" });

  if (!globalAny.__HAPPY_DOM_SUBMIT_BUG_FIXED__) {
    globalAny.__HAPPY_DOM_SUBMIT_BUG_FIXED__ = true;

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
      { capture: true },
    );

    let isInterceptorsRunning = false;
    const originalDispatchEvent = HTMLElement.prototype.dispatchEvent;
    HTMLElement.prototype.dispatchEvent = function (event) {
      if (isInterceptorsRunning) {
        return originalDispatchEvent.call(this, event);
      }
      try {
        isInterceptorsRunning = true;
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
                }),
              );
            }
          }
        }
        return result;
      } finally {
        isInterceptorsRunning = false;
      }
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

  const originalFocus = HTMLElement.prototype.focus;
  let isFocusing = false;
  Object.defineProperty(HTMLElement.prototype, "focus", {
    configurable: true,
    value: function (options?: FocusOptions) {
      if (isFocusing) return;
      try {
        isFocusing = true;
        originalFocus.call(this, options);
      } finally {
        isFocusing = false;
      }
    },
  });
});

afterEach(() => {
  cleanup();
  server.resetHandlers();
  vi.clearAllMocks();
  setHasAnyTriggerBeenClicked(false);
  document.body.removeAttribute("data-scroll-locked");
  document.body.style.pointerEvents = "";
  document.documentElement.style.pointerEvents = "";
  useAuthStore.getState().logout();
});

afterAll(() => server.close());
