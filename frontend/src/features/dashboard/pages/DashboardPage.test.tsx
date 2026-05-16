import { describe, expect, it } from "vitest";
import { render, screen, waitFor, userEvent } from "@/test-utils";
import DashboardPage from "@/features/dashboard/pages/DashboardPage";
import { server } from "@/mocks/server";

describe("DashboardPage", () => {
  it("shows loading skeletons initially", () => {
    render(<DashboardPage />);

    const skeletons = document.querySelectorAll("[class*='animate-pulse']");
    expect(skeletons.length).toBeGreaterThan(0);
  });

  it("renders dashboard after loading", async () => {
    render(<DashboardPage />);

    await waitFor(() => {
      expect(
        screen.getByText("Dashboard Geral"),
      ).toBeInTheDocument();
    });
  });

  it("shows year selector", async () => {
    render(<DashboardPage />);

    await waitFor(() => {
      const currentYear = new Date().getFullYear().toString();
      expect(screen.getByText(currentYear)).toBeInTheDocument();
    });
  });

  it("shows stats cards after loading", async () => {
    render(<DashboardPage />);

    await waitFor(() => {
      expect(
        screen.getByText("Casamentos Ativos"),
      ).toBeInTheDocument();
    });
  });

  it("shows chart and appointments sections", async () => {
    render(<DashboardPage />);

    await waitFor(() => {
      expect(
        screen.getByText("Casamentos por Mês"),
      ).toBeInTheDocument();
      expect(
        screen.getByText("Próximos Compromissos"),
      ).toBeInTheDocument();
    });
  });

  it("shows error state when API fails", async () => {
    const { http, HttpResponse } = await import("msw");
    server.use(
      http.get("*/api/v1/weddings/", () =>
        HttpResponse.json({ detail: "Erro ao carregar painel" }, { status: 500 }),
      ),
    );

    render(<DashboardPage />);

    await waitFor(() => {
      expect(screen.getByText("Erro")).toBeInTheDocument();
      expect(
        screen.getByText("Erro ao carregar painel"),
      ).toBeInTheDocument();
    });
  });

  it("allows changing year with selector", async () => {
    render(<DashboardPage />);

    await waitFor(() => {
      expect(screen.getByText("Casamentos por Mês")).toBeInTheDocument();
    });

    const user = userEvent.setup();
    const prevBtn = screen.getAllByRole("button", { name: "" })[0];
    await user.click(prevBtn);

    const lastYear = new Date().getFullYear() - 1;
    expect(screen.getByText(lastYear.toString())).toBeInTheDocument();
  });
});
