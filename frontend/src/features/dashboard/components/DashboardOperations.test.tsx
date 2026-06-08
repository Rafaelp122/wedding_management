import { describe, expect, it, vi } from "vitest";
import { render, screen, waitFor, userEvent } from "@/test-utils";
import { DashboardOperations } from "@/features/dashboard/components/DashboardOperations";
import { createMockWedding } from "@/test-data";
import { server } from "@/mocks/server";
import { http, HttpResponse } from "msw";

describe("DashboardOperations", () => {
  it("renders headers and tabs list", () => {
    render(<DashboardOperations weddings={[]} />);
    expect(screen.getByText("Checklist de Tarefas Urgentes")).toBeInTheDocument();
    expect(screen.getByRole("tab", { name: /casamentos/i })).toBeInTheDocument();
    expect(screen.getByRole("tab", { name: /tarefas/i })).toBeInTheDocument();
    expect(screen.getByRole("tab", { name: /contratos/i })).toBeInTheDocument();
  });

  it("renders wedding list when active", async () => {
    const user = userEvent.setup();
    const weddings = [
      createMockWedding({ uuid: "w-1", groom_name: "João", bride_name: "Maria", status: "IN_PROGRESS" }),
      createMockWedding({ uuid: "w-2", groom_name: "Pedro", bride_name: "Ana", status: "COMPLETED" }),
    ];
    render(<DashboardOperations weddings={weddings} />);
    const casamentosTab = screen.getByRole("tab", { name: /casamentos/i });
    await user.click(casamentosTab);
    expect(screen.getByText(/João & Maria/)).toBeInTheDocument();
    expect(screen.getByText(/Pedro & Ana/)).toBeInTheDocument();
  });

  it("renders empty state in weddings tab when none provided", async () => {
    const user = userEvent.setup();
    render(<DashboardOperations weddings={[]} />);
    const casamentosTab = screen.getByRole("tab", { name: /casamentos/i });
    await user.click(casamentosTab);
    expect(screen.getByText(/nenhum casamento encontrado/i)).toBeInTheDocument();
  });

  it("switches to Tasks tab and renders tasks list", async () => {
    const user = userEvent.setup();
    const mockTasks = [
      {
        uuid: "t-1",
        title: "Contratar Buffet Fasano",
        description: "Revisar cardápio",
        due_date: "2026-06-15",
        is_completed: false,
        wedding: "w-1",
      },
    ];

    server.use(
      http.get("*/api/v1/scheduler/tasks/", () =>
        HttpResponse.json({ items: mockTasks, count: 1, limit: 100, offset: 0 }),
      ),
    );

    render(<DashboardOperations weddings={[]} />);

    const tasksTab = screen.getByRole("tab", { name: /tarefas/i });
    await user.click(tasksTab);

    // Header title and description should update
    await waitFor(() => {
      expect(screen.getByText("Checklist de Tarefas Urgentes")).toBeInTheDocument();
      expect(screen.getByText("Contratar Buffet Fasano")).toBeInTheDocument();
    });
  });

  it("toggles task status when checking checkbox", async () => {
    const user = userEvent.setup();
    const mockTasks = [
      {
        uuid: "t-1",
        title: "Contratar Banda",
        description: "Pedir orçamentos",
        due_date: "2026-06-20",
        is_completed: false,
        wedding: "w-1",
      },
    ];

    const patchMock = vi.fn();
    server.use(
      http.get("*/api/v1/scheduler/tasks/", () =>
        HttpResponse.json({ items: mockTasks, count: 1, limit: 100, offset: 0 }),
      ),
      http.patch("*/api/v1/scheduler/tasks/:uuid/", async ({ request, params }) => {
        const body = await request.json();
        patchMock(params.uuid, body);
        return HttpResponse.json({ ...mockTasks[0], is_completed: true });
      }),
    );

    render(<DashboardOperations weddings={[]} />);

    const tasksTab = screen.getByRole("tab", { name: /tarefas/i });
    await user.click(tasksTab);

    await waitFor(() => {
      expect(screen.getByText("Contratar Banda")).toBeInTheDocument();
    });

    const checkbox = screen.getByRole("checkbox");
    await user.click(checkbox);

    await waitFor(() => {
      expect(patchMock).toHaveBeenCalledWith("t-1", { is_completed: true });
    });
  });

  it("switches to Contracts tab and renders pending contracts", async () => {
    const user = userEvent.setup();
    const mockContracts = [
      {
        uuid: "c-1",
        supplier_name: "Dj Alok",
        description: "Contrato de Iluminação e som",
        total_amount: "5000.00",
        status: "PENDING",
        wedding: "w-1",
      },
    ];

    server.use(
      http.get("*/api/v1/logistics/contracts/", () =>
        HttpResponse.json({ items: mockContracts, count: 1, limit: 100, offset: 0 }),
      ),
    );

    render(<DashboardOperations weddings={[]} />);

    const contractsTab = screen.getByRole("tab", { name: /contratos/i });
    await user.click(contractsTab);

    await waitFor(() => {
      expect(screen.getByText("Contratos Pendentes com Fornecedores")).toBeInTheDocument();
      expect(screen.getByText("Dj Alok")).toBeInTheDocument();
      expect(screen.getByText("R$ 5.000,00")).toBeInTheDocument();
    });
  });
});
