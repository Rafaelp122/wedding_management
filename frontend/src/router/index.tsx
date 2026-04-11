import { createBrowserRouter, Navigate } from "react-router-dom";
import { lazy, Suspense, type ReactNode } from "react";
import { ProtectedRoute } from "./guards/ProtectedRoute";
import { PublicRoute } from "./guards/PublicRoute";
import { PublicLayout } from "@/components/layouts/PublicLayout";
import { AppLayout } from "@/components/layouts/AppLayout";
import { GlobalError } from "@/components/ui/globalError";
import { LoadingScreen } from "@/components/ui/loadingScreen";

// Implementa o Lazy Loading para separar os bundles
const LandingPage = lazy(() => import("../pages/LandingPage"));
const LoginPage = lazy(() => import("@/features/auth/pages/LoginPage"));
const DashboardPage = lazy(() => import("../pages/DashboardPage"));
const ComingSoonPage = lazy(() => import("../pages/ComingSoonPage"));
const NotFoundPage = lazy(() => import("@/pages/NotFoundPage"));
const SchedulerPage = lazy(
  () => import("@/features/scheduler/pages/SchedulerPage"),
);
const SuppliersPage = lazy(() => import("@/features/suppliers/pages/SuppliersPage"));

// Feature: Weddings
const WeddingsListPage = lazy(
  () => import("@/features/weddings/pages/WeddingsListPage"),
);
const WeddingDetailPage = lazy(
  () => import("@/features/weddings/pages/WeddingDetailPage"),
);

const withLoading = (element: ReactNode) => (
  <Suspense fallback={<LoadingScreen />}>{element}</Suspense>
);

export const router = createBrowserRouter([
  {
    element: <PublicLayout />,
    errorElement: <GlobalError />, // Protege a árvore de rotas públicas
    children: [
      {
        path: "/",
        element: (
          <PublicRoute>
            {withLoading(<LandingPage />)}
          </PublicRoute>
        ),
      },
      {
        path: "/login",
        element: (
          <PublicRoute>
            {withLoading(<LoginPage />)}
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
        element: withLoading(<DashboardPage />),
      },
      {
        path: "/weddings",
        element: withLoading(<WeddingsListPage />),
      },
      {
        path: "/weddings/:uuid",
        element: withLoading(<WeddingDetailPage />),
      },
      {
        path: "/scheduler",
        element: withLoading(<SchedulerPage />),
      },
      {
        path: "/suppliers",
        element: withLoading(<SuppliersPage />),
      },
      {
        path: "/settings",
        element: withLoading(
          <ComingSoonPage
            title="Configurações"
            description="Preferências da conta, organização e integrações ficarão disponíveis aqui."
          />,
        ),
      },
      {
        path: "*",
        element: withLoading(<NotFoundPage />),
      },
      // Adiciona rotas futuras com Lazy Loading aqui
    ],
  },
  {
    path: "*",
    element: withLoading(<NotFoundPage />),
  },
]);
