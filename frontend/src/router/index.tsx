import { createBrowserRouter, Navigate } from "react-router-dom";
import { lazy, Suspense } from "react";
import { ProtectedRoute } from "./guards/ProtectedRoute";
import { PublicRoute } from "./guards/PublicRoute";
import { PublicLayout } from "@/components/layouts/PublicLayout";
import { AppLayout } from "@/components/layouts/AppLayout";
import { GlobalError } from "@/components/ui/globalError";
import { LoadingScreen } from "@/components/ui/loadingScreen";

// Implementa o Lazy Loading para separar os bundles
const LandingPage = lazy(() => import("../pages/LandingPage"));
const LoginPage = lazy(() => import("../pages/LoginPage"));
const DashboardPage = lazy(() => import("../pages/DashboardPage"));
const ComingSoonPage = lazy(() => import("../pages/ComingSoonPage"));
const NotFoundPage = lazy(() => import("@/pages/NotFoundPage"));

export const router = createBrowserRouter([
  {
    element: <PublicLayout />,
    errorElement: <GlobalError />, // Protege a árvore de rotas públicas
    children: [
      {
        path: "/",
        element: (
          <PublicRoute>
            <Suspense fallback={<LoadingScreen />}>
              <LandingPage />
            </Suspense>
          </PublicRoute>
        ),
      },
      {
        path: "/login",
        element: (
          <PublicRoute>
            <Suspense fallback={<LoadingScreen />}>
              <LoginPage />
            </Suspense>
          </PublicRoute>
        ),
      },
    ],
  },
  {
    element: (
      <ProtectedRoute>
        <AppLayout />
      </ProtectedRoute>
    ),
    errorElement: <GlobalError />, // Protege a árvore de rotas da aplicação
    children: [
      {
        path: "/app",
        element: <Navigate to="/dashboard" replace />,
      },
      {
        path: "/dashboard",
        element: (
          <Suspense fallback={<LoadingScreen />}>
            <DashboardPage />
          </Suspense>
        ),
      },
      {
        path: "/weddings",
        element: (
          <Suspense fallback={<LoadingScreen />}>
            <ComingSoonPage
              title="Casamentos"
              description="A gestão detalhada de casamentos será disponibilizada em breve."
            />
          </Suspense>
        ),
      },
      {
        path: "/scheduler",
        element: (
          <Suspense fallback={<LoadingScreen />}>
            <ComingSoonPage
              title="Agenda"
              description="A visualização completa da agenda será disponibilizada em breve."
            />
          </Suspense>
        ),
      },
      {
        path: "/logistics/contracts",
        element: (
          <Suspense fallback={<LoadingScreen />}>
            <ComingSoonPage
              title="Contratos"
              description="O módulo de contratos está em preparação e ficará disponível em breve."
            />
          </Suspense>
        ),
      },
      {
        path: "/logistics/items",
        element: (
          <Suspense fallback={<LoadingScreen />}>
            <ComingSoonPage
              title="Itens & Estoque"
              description="O controle de itens e estoque será disponibilizado em breve."
            />
          </Suspense>
        ),
      },
      {
        path: "/finances/budgets",
        element: (
          <Suspense fallback={<LoadingScreen />}>
            <ComingSoonPage
              title="Financeiro"
              description="A área financeira detalhada será disponibilizada em breve."
            />
          </Suspense>
        ),
      },
      {
        path: "/finances/expenses",
        element: (
          <Suspense fallback={<LoadingScreen />}>
            <ComingSoonPage
              title="Despesas"
              description="A gestão detalhada de despesas será disponibilizada em breve."
            />
          </Suspense>
        ),
      },
      {
        path: "*",
        element: (
          <Suspense fallback={<LoadingScreen />}>
            <NotFoundPage />
          </Suspense>
        ),
      },
      // Adiciona rotas futuras com Lazy Loading aqui
    ],
  },
  {
    path: "*",
    element: (
      <Suspense fallback={<LoadingScreen />}>
        <NotFoundPage />
      </Suspense>
    ),
  },
]);
