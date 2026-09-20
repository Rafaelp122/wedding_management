import { describe, expect, it, vi } from "vitest";
import { render, screen, waitFor, userEvent } from "@/test-utils";
import { DashboardOperations } from "@/features/dashboard/components/DashboardOperations";
import { server } from "@/mocks/server";
import { http, HttpResponse } from "msw";

describe("DashboardOperations", () => {
  it("renders headers and tabs list", () => {
    server.use(
      http.get("*/api/v1/dashboard/operations/", () =>
        HttpResponse.json({
          upcoming_weddings: [],
          urgent_tasks: [],
          pending_contracts: [],
        }),
      ),
    );

    render(<DashboardOperations />);
    expect(screen.getByText("Checklist de Tarefas Urgentes")).toBeInTheDocument();
    expect(screen.getByRole("tab", { name: /casamentos/i })).toBeInTheDocument();
    expect(screen.getByRole("tab", { name: /tarefas/i })).toBeInTheDocument();
    expect(screen.getByRole("tab", { name: /contratos/i })).toBeInTheDocument();
  });

  it("renders wedding list when active", async () => {
    const user = userEvent.setup();
    server.use(
      http.get("*/api/v1/dashboard/operations/", () =>
        HttpResponse.json({
          upcoming_weddings: [
            {
              uuid: "w-1",
              bride_name: "Maria",
              groom_name: "João",
              date: "2026-06-15",
              days_until: 45,
            },
            {
              uuid: "w-2",
              bride_name: "Ana",
              groom_name: "Pedro",
              date: "2026-07-20",
              days_until: 80,
            },
          ],
          urgent_tasks: [],
          pending_contracts: [],
        }),
      ),
    );

    render(<DashboardOperations />);
    const casamentosTab = screen.getByRole("tab", { name: /casamentos/i });
    await user.click(casamentosTab);
    expect(screen.getByText(/Maria & João/)).toBeInTheDocument();
    expect(screen.getByText(/Ana & Pedro/)).toBeInTheDocument();
  });

  it("renders empty state in weddings tab when none provided", async () => {
    const user = userEvent.setup();
    server.use(
      http.get("*/api/v1/dashboard/operations/", () =>
        HttpResponse.json({
          upcoming_weddings: [],
          urgent_tasks: [],
          pending_contracts: [],
        }),
      ),
    );

    render(<DashboardOperations />);
    const casamentosTab = screen.getByRole("tab", { name: /casamentos/i });
    await user.click(casamentosTab);
    expect(screen.getByText(/nenhum casamento encontrado/i)).toBeInTheDocument();
  });

  it("switches to Tasks tab and renders tasks list", async () => {
    const user = userEvent.setup();
    server.use(
      http.get("*/api/v1/dashboard/operations/", () =>
        HttpResponse.json({
          upcoming_weddings: [],
          urgent_tasks: [
            {
              uuid: "t-1",
              title: "Contratar Buffet Fasano",
              wedding_name: "Maria e João",
              due_date: "2026-06-15",
            },
          ],
          pending_contracts: [],
        }),
      ),
    );

    render(<DashboardOperations />);

    const tasksTab = screen.getByRole("tab", { name: /tarefas/i });
    await user.click(tasksTab);

    await waitFor(() => {
      expect(screen.getByText("Checklist de Tarefas Urgentes")).toBeInTheDocument();
      expect(screen.getByText("Contratar Buffet Fasano")).toBeInTheDocument();
      expect(screen.getByText(/Maria e João/)).toBeInTheDocument();
    });
  });

  it("toggles task status when checking checkbox", async () => {
    const user = userEvent.setup();
    const completeMock = vi.fn();

    server.use(
      http.get("*/api/v1/dashboard/operations/", () =>
        HttpResponse.json({
          upcoming_weddings: [],
          urgent_tasks: [
            {
              uuid: "t-1",
              title: "Contratar Banda",
              wedding_name: "Maria e João",
              due_date: "2026-06-20",
            },
          ],
          pending_contracts: [],
        }),
      ),
      http.post("*/api/v1/scheduler/tasks/:uuid/complete/", ({ params }) => {
        completeMock(params.uuid);
        return HttpResponse.json({ uuid: params.uuid, is_completed: true });
      }),
    );

    render(<DashboardOperations />);

    const tasksTab = screen.getByRole("tab", { name: /tarefas/i });
    await user.click(tasksTab);

    await waitFor(() => {
      expect(screen.getByText("Contratar Banda")).toBeInTheDocument();
    });

    const checkbox = screen.getByRole("checkbox");
    await user.click(checkbox);

    await waitFor(() => {
      expect(completeMock).toHaveBeenCalledWith("t-1");
    });
  });

  it("switches to Contracts tab and renders pending contracts", async () => {
    const user = userEvent.setup();
    server.use(
      http.get("*/api/v1/dashboard/operations/", () =>
        HttpResponse.json({
          upcoming_weddings: [],
          urgent_tasks: [],
          pending_contracts: [
            {
              uuid: "c-1",
              supplier_name: "Dj Alok",
              wedding_name: "Maria e João",
              total_amount: "5000.00",
              status: "PENDING",
            },
          ],
        }),
      ),
    );

    render(<DashboardOperations />);

    const contractsTab = screen.getByRole("tab", { name: /contratos/i });
    await user.click(contractsTab);

    await waitFor(() => {
      expect(screen.getByText("Contratos Pendentes com Fornecedores")).toBeInTheDocument();
      expect(screen.getByText("Dj Alok")).toBeInTheDocument();
      expect(screen.getByText("5.000,00")).toBeInTheDocument();
      expect(screen.getByText(/Maria e João/)).toBeInTheDocument();
    });
  });
});
