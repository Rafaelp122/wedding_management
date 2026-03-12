import { Navigate } from "react-router-dom";
import { useAuthStore } from "@/stores/authStore";
import type { ReactNode } from "react";

interface RouteGuardProps {
  children: ReactNode;
}

export const PublicRoute = ({ children }: RouteGuardProps) => {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  return children;
};
