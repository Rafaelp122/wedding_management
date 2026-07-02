import "./instrument"; // Must be first

import React from "react";
import ReactDOM from "react-dom/client";
import * as Sentry from "@sentry/react";
import {
  QueryCache,
  QueryClient,
  QueryClientProvider,
} from "@tanstack/react-query";
import { ReactQueryDevtools } from "@tanstack/react-query-devtools";
import { RouterProvider } from "react-router-dom"; // O substituto do BrowserRouter
import { toast } from "sonner";
import { ThemeProvider } from "next-themes";

import { getApiErrorInfo } from "@/api/error-utils";
import { router } from "./router"; // Importando sua nova configuração
import { Toaster } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import "./index.css";

const queryClient = new QueryClient({
  queryCache: new QueryCache({
    onError: (error) => {
      const { status, message } = getApiErrorInfo(
        error,
        "Não foi possível carregar os dados solicitados.",
      );

      // 401 já entra no fluxo de refresh/logout do Axios.
      if (status === 401) {
        return;
      }

      // Reporta erros inesperados ao Sentry (404 e erros de rede são
      // filtrados pelo beforeSend no instrument.ts).
      if (error instanceof Error && status !== 404) {
        Sentry.captureException(error, {
          tags: { source: "react-query", http_status: String(status ?? 0) },
        });
      }

      toast.error(message);
    },
  }),
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5,
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

ReactDOM.createRoot(document.getElementById("root")!, {
  onUncaughtError: Sentry.reactErrorHandler(),
  onRecoverableError: Sentry.reactErrorHandler(),
}).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
        <TooltipProvider>
          <RouterProvider router={router} />
          <Toaster />
          <ReactQueryDevtools initialIsOpen={false} />
        </TooltipProvider>
      </ThemeProvider>
    </QueryClientProvider>
  </React.StrictMode>,
);
