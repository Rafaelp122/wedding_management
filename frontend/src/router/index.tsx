import { createBrowserRouter, Navigate } from "react-router-dom";
import { lazy, Suspense, type ReactNode } from "react";
import { ProtectedRoute } from "./guards/ProtectedRoute";
import { PublicRoute } from "./guards/PublicRoute";
import { PublicLayout } from "@/components/layouts/PublicLayout";
import { AppLayout } from "@/components/layouts/AppLayout";
import { GlobalError } from "@/components/ui/globalError";
import { LoadingScreen } from "@/components/ui/loadingScreen";

const LoginPage = lazy(() => import("@/features/auth/pages/LoginPage"));
const RegisterPage = lazy(() => import("@/features/auth/pages/RegisterPage"));
const DashboardPage = lazy(
  () => import("@/features/dashboard/pages/DashboardPage"),
);
const ComingSoonPage = lazy(() => import("@/components/coming-soon"));
const NotFoundPage = lazy(() => import("@/components/not-found"));
const SchedulerPage = lazy(
  () => import("@/features/scheduler/pages/SchedulerPage"),
);
const SuppliersPage = lazy(() => import("@/features/logistics/pages/SuppliersPage"));

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
        element: <Navigate to="/login" replace />,
      },
      {
        path: "/login",
        element: (
          <PublicRoute>
            {withLoading(<LoginPage />)}
          </PublicRoute>
        ),
      },
      {
        path: "/register",
        element: (
          <PublicRoute>
            {withLoading(<RegisterPage />)}
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
