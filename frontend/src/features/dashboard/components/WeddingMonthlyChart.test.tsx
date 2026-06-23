import { describe, expect, it, vi } from "vitest";
import { render, screen, waitFor, userEvent } from "@/test-utils";
import { WeddingMonthlyChart } from "@/features/dashboard/components/WeddingMonthlyChart";
import { server } from "@/mocks/server";
import { http, HttpResponse } from "msw";

describe("WeddingMonthlyChart", () => {
  it("shows empty state for year with no weddings", () => {
    server.use(
      http.get("*/api/v1/weddings/by-month/", () =>
        HttpResponse.json([]),
      ),
    );

    render(
      <WeddingMonthlyChart
        selectedYear={2025}
        onYearChange={vi.fn()}
      />,
    );

    expect(
      screen.getByText(/nenhum casamento agendado para 2025/i),
    ).toBeInTheDocument();
  });

  it("renders chart container when data exists", () => {
    server.use(
      http.get("*/api/v1/weddings/by-month/", () =>
        HttpResponse.json([{ month: 6, count: 1 }]),
      ),
    );

    render(
      <WeddingMonthlyChart
        selectedYear={2025}
        onYearChange={vi.fn()}
      />,
    );

    expect(screen.getByText("Casamentos por Mês")).toBeInTheDocument();
    expect(
      screen.getByText(/Distribuição de casamentos ao longo de 2025/),
    ).toBeInTheDocument();
  });

  it("renders wedding bars for populated data", () => {
    server.use(
      http.get("*/api/v1/weddings/by-month/", () =>
        HttpResponse.json([
          { month: 1, count: 2 },
          { month: 6, count: 1 },
        ]),
      ),
    );

    render(
      <WeddingMonthlyChart
        selectedYear={2025}
        onYearChange={vi.fn()}
      />,
    );

    expect(screen.getByText("Casamentos por Mês")).toBeInTheDocument();
    expect(
      screen.getByText(/Distribuição de casamentos ao longo de 2025/),
    ).toBeInTheDocument();
  });

  it("switches to Financeiro tab and shows expected content", async () => {
    const user = userEvent.setup();
    server.use(
      http.get("*/api/v1/finances/installments/", () =>
        HttpResponse.json({ items: [], count: 0, limit: 200, offset: 0 }),
      ),
    );

    render(
      <WeddingMonthlyChart
        selectedYear={2025}
        onYearChange={vi.fn()}
      />,
    );

    const financeTab = screen.getByRole("tab", { name: /financeiro/i });
    await user.click(financeTab);

    await waitFor(() => {
      expect(screen.getByText("Fluxo de Caixa Mensal")).toBeInTheDocument();
      expect(screen.getByText(/Receitas recebidas vs. previstas para 2025/)).toBeInTheDocument();
    });
  });

  it("renders cash flow bars with populated installment data", async () => {
    const user = userEvent.setup();
    server.use(
      http.get("*/api/v1/finances/installments/", () =>
        HttpResponse.json({
          items: [
            {
              uuid: "inst-1",
              installment_number: 1,
              amount: "3000.00",
              due_date: "2025-01-15",
              status: "PAID",
              expense: "exp-1",
              wedding: "w1",
            },
            {
              uuid: "inst-2",
              installment_number: 2,
              amount: "2000.00",
              due_date: "2025-01-20",
              status: "PENDING",
              expense: "exp-2",
              wedding: "w1",
            },
            {
              uuid: "inst-3",
              installment_number: 1,
              amount: "5000.00",
              due_date: "2025-06-10",
              status: "PAID",
              expense: "exp-3",
              wedding: "w2",
            },
          ],
          count: 3,
          limit: 200,
          offset: 0,
        }),
      ),
    );

    render(
      <WeddingMonthlyChart
        selectedYear={2025}
        onYearChange={vi.fn()}
      />,
    );

    const financeTab = screen.getByRole("tab", { name: /financeiro/i });
    await user.click(financeTab);

    await waitFor(() => {
      expect(screen.getByText("Fluxo de Caixa Mensal")).toBeInTheDocument();
    });
  });

  it("switches to Tarefas tab and shows expected content", async () => {
    const user = userEvent.setup();
    server.use(
      http.get("*/api/v1/scheduler/tasks/", () =>
        HttpResponse.json({ items: [], count: 0, limit: 200, offset: 0 }),
      ),
    );

    render(
      <WeddingMonthlyChart
        selectedYear={2025}
        onYearChange={vi.fn()}
      />,
    );

    const tasksTab = screen.getByRole("tab", { name: /tarefas/i });
    await user.click(tasksTab);

    await waitFor(() => {
      expect(screen.getByText("Progresso de Cronograma")).toBeInTheDocument();
      expect(screen.getByText(/Nível de conclusão do checklist dos casamentos de 2025/)).toBeInTheDocument();
    });
  });

  it("renders task progress bars with populated data", async () => {
    const user = userEvent.setup();
    server.use(
      http.get("*/api/v1/scheduler/tasks/", () =>
        HttpResponse.json({
          items: [
            { uuid: "t1", title: "Tarefa 1", is_completed: true, wedding: "w1" },
            { uuid: "t2", title: "Tarefa 2", is_completed: false, wedding: "w1" },
            { uuid: "t3", title: "Tarefa 3", is_completed: true, wedding: "w2" },
            { uuid: "t4", title: "Tarefa 4", is_completed: true, wedding: "w2" },
            { uuid: "t5", title: "Tarefa 5", is_completed: false, wedding: "w2" },
          ],
          count: 5,
          limit: 200,
          offset: 0,
        }),
      ),
    );

    render(
      <WeddingMonthlyChart
        selectedYear={2025}
        onYearChange={vi.fn()}
      />,
    );

    const tasksTab = screen.getByRole("tab", { name: /tarefas/i });
    await user.click(tasksTab);

    await waitFor(() => {
      expect(screen.getByText("Progresso de Cronograma")).toBeInTheDocument();
    });
  });

  it("calls onYearChange when navigation buttons are clicked", async () => {
    const user = userEvent.setup();
    const onYearChange = vi.fn();
    render(
      <WeddingMonthlyChart
        selectedYear={2025}
        onYearChange={onYearChange}
      />,
    );

    const prevBtn = screen.getByLabelText("Ano anterior");
    await user.click(prevBtn);
    expect(onYearChange).toHaveBeenCalledWith(2024);

    const nextBtn = screen.getByLabelText("Próximo ano");
    await user.click(nextBtn);
    expect(onYearChange).toHaveBeenCalledWith(2026);
  });
});
