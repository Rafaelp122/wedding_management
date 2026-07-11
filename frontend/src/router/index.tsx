import { createBrowserRouter, Navigate } from "react-router-dom";
import * as Sentry from "@sentry/react";
import { lazy, Suspense, type ReactNode } from "react";
import { ProtectedRoute } from "./guards/ProtectedRoute";
import { PublicRoute } from "./guards/PublicRoute";
import { AppLayout } from "@/components/layouts/AppLayout";
import { GlobalError } from "@/components/ui/globalError";
import { LoadingScreen } from "@/components/ui/loadingScreen";

// Static imports for main pages — loaded eagerly for instant navigation
import LoginPage from "@/features/auth/pages/LoginPage";
import RegisterPage from "@/features/auth/pages/RegisterPage";
import DashboardPage from "@/features/dashboard/pages/DashboardPage";
import SchedulerPage from "@/features/scheduler/pages/SchedulerPage";
import SuppliersPage from "@/features/logistics/pages/SuppliersPage";
import WeddingsListPage from "@/features/weddings/pages/WeddingsListPage";
import WeddingDetailPage from "@/features/weddings/pages/WeddingDetailPage";

// Lazy imports for rarely accessed pages
const ComingSoonPage = lazy(() => import("@/components/coming-soon"));
const NotFoundPage = lazy(() => import("@/components/not-found"));

const withLoading = (element: ReactNode) => (
  <Suspense fallback={<LoadingScreen />}>{element}</Suspense>
);

const sentryCreateBrowserRouter = Sentry.wrapCreateBrowserRouterV7(createBrowserRouter);

export const router = sentryCreateBrowserRouter([
  // Auth routes — standalone with their own split-screen layout
  {
    path: "/login",
    element: (
      <PublicRoute>
        <LoginPage />
      </PublicRoute>
    ),
  },
  {
    path: "/register",
    element: (
      <PublicRoute>
        <RegisterPage />
      </PublicRoute>
    ),
  },
  {
    path: "/",
    element: <Navigate to="/login" replace />,
  },
  {
    element: (
      <ProtectedRoute>
        <AppLayout />
      </ProtectedRoute>
    ),
    errorElement: <GlobalError />,
    children: [
      {
        path: "/app",
        element: <Navigate to="/dashboard" replace />,
      },
      {
        path: "/dashboard",
        element: <DashboardPage />,
      },
      {
        path: "/weddings",
        element: <WeddingsListPage />,
      },
      {
        path: "/weddings/:uuid",
        element: <WeddingDetailPage />,
      },
      {
        path: "/scheduler",
        element: <SchedulerPage />,
      },
      {
        path: "/suppliers",
        element: <SuppliersPage />,
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
    ],
  },
  {
    path: "*",
    element: withLoading(<NotFoundPage />),
  },
]);
