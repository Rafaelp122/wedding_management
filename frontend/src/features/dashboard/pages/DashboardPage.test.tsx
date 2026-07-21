
import { describe, expect, it, beforeEach, vi } from "vitest";
import { render, screen, waitFor, userEvent } from "@/test-utils";
import DashboardPage from "@/features/dashboard/pages/DashboardPage";

import { server } from "@/mocks/server";
import { http, HttpResponse } from "msw";

const mockNavigate = vi.hoisted(() => vi.fn());
vi.mock("react-router-dom", async (importOriginal) => {
  const actual = await importOriginal<typeof import("react-router-dom")>();
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

describe("DashboardPage", () => {
  beforeEach(() => {
    mockNavigate.mockReset();
    server.use(
      http.get("*/api/v1/dashboard/summary/", () => {
        return HttpResponse.json({
          pending_installments_7d: "0",
          urgent_tasks_count: 0,
          overdue_installments_amount: "0",
          overdue_installments_count: 0,
          pending_contracts_count: 0,
          critical_weddings: [],
        });
      }),
      http.get("*/api/v1/dashboard/wedding/:uuid/", () => {
        return HttpResponse.json({
          days_until_wedding: 0,
          budget_percentage_used: 0,
          tasks_completed: 0,
          tasks_total: 0,
          contracts_signed: 0,
          contracts_total: 0,
          upcoming_installments: [],
          urgent_tasks: [],
          categories_summary: [],
        });
      })
    );
  });

  it("shows loading skeletons initially", () => {
    render(<DashboardPage />);

    const skeletons = document.querySelectorAll("[class*='animate-pulse']");
    expect(skeletons.length).toBeGreaterThan(0);
  });

  it("renders dashboard after loading", async () => {
    render(<DashboardPage />);

    await waitFor(() => {
      expect(
        screen.getByText(/Aqui está o panorama financeiro e de eventos para hoje/i),
      ).toBeInTheDocument();
    });
  });

  it("shows year selector", async () => {
    render(<DashboardPage />);

    await waitFor(() => {
      expect(screen.getByText("Casamentos por Mês")).toBeInTheDocument();
    }, { timeout: 5000 });

    const currentYear = new Date().getFullYear().toString();
    expect(screen.getByText(currentYear)).toBeInTheDocument();
  });

  it("shows stats cards after loading", async () => {
    render(<DashboardPage />);

    await waitFor(() => {
      expect(
        screen.getByText("Parcelas Vencidas"),
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
        screen.getByText("Agenda"),
      ).toBeInTheDocument();
    }, { timeout: 5000 });
  });

  it("shows error state when API fails", async () => {
    server.use(
      http.get("*/api/v1/weddings/lookup/", () =>
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
    }, { timeout: 5000 });

    const user = userEvent.setup();
    const prevBtn = screen.getByRole("button", { name: /ano anterior/i });
    await user.click(prevBtn);

    const lastYear = new Date().getFullYear() - 1;
    expect(screen.getByText(lastYear.toString())).toBeInTheDocument();
  });

  it("allows filtering by a specific wedding", async () => {
    render(<DashboardPage />);

    await waitFor(() => {
      expect(document.getElementById("wedding-filter")).toBeInTheDocument();
    }, { timeout: 5000 });

    const trigger = document.getElementById("wedding-filter")!;
    const user = userEvent.setup();
    await user.click(trigger);

    const options = await screen.findAllByRole("option");
    expect(options.length).toBeGreaterThan(1);
  });

  it("navigates to wedding detail page and finances tab when header buttons are clicked", async () => {
    render(<DashboardPage />);

    await waitFor(() => {
      expect(document.getElementById("wedding-filter")).toBeInTheDocument();
    }, { timeout: 5000 });

    const trigger = document.getElementById("wedding-filter")!;
    const user = userEvent.setup();
    await user.click(trigger);

    const options = await screen.findAllByRole("option");
    await user.click(options[1]);

    const openBtn = await screen.findByRole("button", { name: /abrir casamento/i });
    await user.click(openBtn);
    await waitFor(() => {
      expect(mockNavigate).toHaveBeenLastCalledWith(expect.stringMatching(/\/weddings\/[A-Za-z0-9_-]+/));
    });

    const financesBtn = screen.getByRole("button", { name: /finanças/i });
    await user.click(financesBtn);
    await waitFor(() => {
      expect(mockNavigate).toHaveBeenLastCalledWith(expect.stringMatching(/\/weddings\/[A-Za-z0-9_-]+\?tab=finances/));
    });
  });
});
