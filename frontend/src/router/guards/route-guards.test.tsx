import { beforeEach, describe, expect, it } from "vitest";
import { useLocation } from "react-router-dom";

import { render, screen, waitFor } from "@/test-utils";
import { useAuthStore } from "@/stores/authStore";
import { ProtectedRoute } from "./ProtectedRoute";
import { PublicRoute } from "./PublicRoute";

function LocationProbe() {
  return <output aria-label="current path">{useLocation().pathname}</output>;
}

describe("route guards", () => {
  beforeEach(() => useAuthStore.getState().logout());

  it("redirects unauthenticated users to login", async () => {
    render(
      <>
        <ProtectedRoute><p>Área protegida</p></ProtectedRoute>
        <LocationProbe />
      </>,
      { initialEntries: ["/dashboard"] },
    );

    await waitFor(() => expect(screen.getByLabelText("current path")).toHaveTextContent("/login"));
    expect(screen.queryByText("Área protegida")).not.toBeInTheDocument();
  });

  it("renders protected content for authenticated users", () => {
    useAuthStore.setState({ isAuthenticated: true });

    render(<ProtectedRoute><p>Área protegida</p></ProtectedRoute>);

    expect(screen.getByText("Área protegida")).toBeInTheDocument();
  });

  it("redirects authenticated users away from public routes", async () => {
    useAuthStore.setState({ isAuthenticated: true });

    render(
      <>
        <PublicRoute><p>Área pública</p></PublicRoute>
        <LocationProbe />
      </>,
      { initialEntries: ["/login"] },
    );

    await waitFor(() => expect(screen.getByLabelText("current path")).toHaveTextContent("/dashboard"));
    expect(screen.queryByText("Área pública")).not.toBeInTheDocument();
  });

  it("renders public content for unauthenticated users", () => {
    render(<PublicRoute><p>Área pública</p></PublicRoute>);

    expect(screen.getByText("Área pública")).toBeInTheDocument();
  });
});
