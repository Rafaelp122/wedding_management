import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, renderHook } from "@testing-library/react";
import type { RenderOptions, RenderResult } from "@testing-library/react";
import { ThemeProvider } from "next-themes";
import type { ReactElement, ReactNode } from "react";
import { createMemoryRouter, RouterProvider } from "react-router-dom";
import { Toaster } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";

function createTestQueryClient() {
  return new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
      mutations: {
        retry: false,
      },
    },
  });
}

interface WrapperOptions {
  initialEntries?: string[];
  queryClient?: QueryClient;
}

function createWrapper(options: WrapperOptions = {}) {
  const { initialEntries = ["/"], queryClient = createTestQueryClient() } = options;

  return function Wrapper({ children }: { children: ReactNode }) {
    const router = createMemoryRouter(
      [{ path: "*", element: <>{children}</> }],
      { initialEntries },
    );

    return (
      <QueryClientProvider client={queryClient}>
        <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
          <TooltipProvider delayDuration={0}>
            <RouterProvider router={router} />
            <Toaster />
          </TooltipProvider>
        </ThemeProvider>
      </QueryClientProvider>
    );
  };
}

function customRender(
  ui: ReactElement,
  options?: Omit<RenderOptions, "wrapper"> & WrapperOptions,
): RenderResult {
  const { initialEntries, queryClient, ...renderOptions } = options ?? {};
  return render(ui, {
    wrapper: createWrapper({ initialEntries, queryClient }),
    ...renderOptions,
  });
}

function customRenderHook<Result, Props>(
  hook: (props: Props) => Result,
  options?: Omit<Parameters<typeof renderHook>[1], "wrapper"> & WrapperOptions,
) {
  const { initialEntries, queryClient, ...hookOptions } = options ?? {};
  return renderHook(hook, {
    wrapper: createWrapper({ initialEntries, queryClient }),
    ...hookOptions,
  });
}

export { customRender as render, customRenderHook as renderHook };
export { screen, within, waitFor, act, fireEvent } from "@testing-library/react";
import { userEvent as originalUserEvent } from "@testing-library/user-event";

const customUserEvent = {
  ...originalUserEvent,
  setup(options?: Parameters<typeof originalUserEvent.setup>[0]) {
    return originalUserEvent.setup({
      pointerEventsCheck: 0, // Disable pointer-events checks for Dialogs in Happy DOM
      ...options,
    });
  },
};

export { customUserEvent as userEvent };
export { server } from "@/mocks/server";
