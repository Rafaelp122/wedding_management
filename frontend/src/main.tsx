import React from "react";
import ReactDOM from "react-dom/client";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ReactQueryDevtools } from "@tanstack/react-query-devtools";
import { BrowserRouter } from "react-router-dom";
import App from "./App";
import "./index.css";

async function enableMocking() {
  if (
    import.meta.env.MODE !== "development" ||
    import.meta.env.VITE_ENABLE_MOCKS !== "true"
  ) {
    return;
  }

  // SetupWorker da biblioteca MSW
  const { setupWorker } = await import("msw/browser");

  // Handlers de cada módulo gerado
  // O Orval gera funções chamadas get[NomeDaTag]MockHandlers
  const { getAuthMock } = await import("./api/generated/auth/auth.msw");
  const { getFinancesMock } =
    await import("./api/generated/finances/finances.msw");
  const { getLogisticsMock } =
    await import("./api/generated/logistics/logistics.msw");
  const { getSchedulerMock } =
    await import("./api/generated/scheduler/scheduler.msw");
  const { getWeddingsMock } =
    await import("./api/generated/weddings/weddings.msw");

  // Worker unindo todos os interceptores
  const worker = setupWorker(
    ...getAuthMock(),
    ...getFinancesMock(),
    ...getLogisticsMock(),
    ...getSchedulerMock(),
    ...getWeddingsMock(),
  );

  return worker.start({
    onUnhandledRequest: "bypass",
  });
}

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5,
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

enableMocking().then(() => {
  ReactDOM.createRoot(document.getElementById("root")!).render(
    <React.StrictMode>
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <App />
        </BrowserRouter>
        <ReactQueryDevtools initialIsOpen={false} />
      </QueryClientProvider>
    </React.StrictMode>,
  );
});
