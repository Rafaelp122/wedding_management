import React from "react";
import ReactDOM from "react-dom/client";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ReactQueryDevtools } from "@tanstack/react-query-devtools";
import { BrowserRouter } from "react-router-dom";
import App from "./App";
import "./index.css";

// Mantemos o seu cliente com as configurações de cache inteligentes
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // Dados frescos por 5 minutos
      retry: 1, // Se falhar (ex: 401), o nosso interceptor resolve. Não precisa o Query ficar spamando.
      refetchOnWindowFocus: false, // Não irrita o backend toda vez que o usuário der alt+tab
    },
  },
});

// Sem mocks. Direto para a renderização real.
ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <App />
      </BrowserRouter>
      {/* Devtools ativado, seu melhor amigo para debugar os hooks do Orval */}
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  </React.StrictMode>,
);
