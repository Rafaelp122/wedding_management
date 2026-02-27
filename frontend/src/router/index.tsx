import { createBrowserRouter, Navigate } from "react-router-dom";

// Layouts
import { PublicLayout } from "@/components/layouts/PublicLayout";
import { AppLayout } from "@/components/layouts/AppLayout";

// Guards
import { ProtectedRoute } from "@/router/guards/ProtectedRoute";
import { PublicRoute } from "@/router/guards/PublicRoute";

// Pages (Orquestradores)
import LandingPage from "@/pages/LandingPage";
import LoginPage from "@/pages/LoginPage";
import DashboardPage from "@/pages/DashboardPage";

// Nota: Conforme você for criando as outras páginas, importe-as aqui
// import WeddingsPage from "@/pages/WeddingsPage";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <PublicLayout />,
    children: [
      {
        index: true, // Isso faz com que a LandingPage seja o "/"
        element: <LandingPage />,
      },
      {
        path: "login",
        element: (
          <PublicRoute>
            <LoginPage />
          </PublicRoute>
        ),
      },
      {
        path: "register",
        element: (
          <PublicRoute>
            {/* <RegisterPage /> */}
            <div className="p-8 text-center">
              Página de Registro em breve...
            </div>
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
    children: [
      {
        path: "dashboard",
        element: <DashboardPage />,
      },
      {
        path: "weddings",
        element: (
          <div className="p-6">
            <h1>Gestão de Casamentos</h1>
          </div>
        ),
      },
      {
        path: "scheduler",
        element: (
          <div className="p-6">
            <h1>Agenda de Eventos</h1>
          </div>
        ),
      },
      {
        path: "logistics",
        children: [
          {
            path: "contracts",
            element: (
              <div className="p-6">
                <h1>Contratos</h1>
              </div>
            ),
          },
          {
            path: "items",
            element: (
              <div className="p-6">
                <h1>Itens & Estoque</h1>
              </div>
            ),
          },
        ],
      },
      {
        path: "finances",
        children: [
          {
            path: "budgets",
            element: (
              <div className="p-6">
                <h1>Orçamentos</h1>
              </div>
            ),
          },
          {
            path: "expenses",
            element: (
              <div className="p-6">
                <h1>Despesas</h1>
              </div>
            ),
          },
        ],
      },
    ],
  },
  {
    path: "*",
    element: <Navigate to="/" replace />,
  },
]);
