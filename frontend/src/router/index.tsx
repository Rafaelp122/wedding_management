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
const AgendaPage = lazy(() => import("@/features/scheduler/pages/AgendaPage"));
const SuppliersPage = lazy(() => import("@/features/suppliers/pages/SuppliersPage"));

// Feature: Weddings
const WeddingsListPage = lazy(
  () => import("@/features/weddings/pages/WeddingsListPage"),
);
const WeddingDetailPage = lazy(
  () => import("@/features/weddings/pages/WeddingDetailPage"),
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
            <WeddingsListPage />
          </Suspense>
        ),
      },
      {
        path: "/weddings/:uuid",
        element: (
          <Suspense fallback={<LoadingScreen />}>
            <WeddingDetailPage />
          </Suspense>
        ),
      },
      {
        path: "/agenda",
        element: (
          <Suspense fallback={<LoadingScreen />}>
            <AgendaPage />
          </Suspense>
        ),
      },
      {
        path: "/suppliers",
        element: (
          <Suspense fallback={<LoadingScreen />}>
            <SuppliersPage />
          </Suspense>
        ),
      },
      {
        path: "/settings",
        element: (
          <Suspense fallback={<LoadingScreen />}>
            <ComingSoonPage
              title="Configurações"
              description="Preferências da conta, organização e integrações ficarão disponíveis aqui."
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
