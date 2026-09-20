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
      http.get("*/api/v1/dashboard/chart/cash-flow/", () =>
        HttpResponse.json([]),
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
      http.get("*/api/v1/dashboard/chart/cash-flow/", () =>
        HttpResponse.json([
          {
            month: 1,
            paid: "3000.00",
            pending: "2000.00",
          },
          {
            month: 6,
            paid: "5000.00",
            pending: "0.00",
          },
        ]),
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
      http.get("*/api/v1/dashboard/chart/task-progress/", () =>
        HttpResponse.json([]),
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
      http.get("*/api/v1/dashboard/chart/task-progress/", () =>
        HttpResponse.json([
          {
            wedding_uuid: "w1",
            wedding_name: "Ana e Carlos",
            total_tasks: 10,
            completed_tasks: 8,
            progress_pct: 80,
          },
        ]),
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
