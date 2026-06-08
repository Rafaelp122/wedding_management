import { describe, expect, it, vi } from "vitest";
import { render, screen, waitFor, userEvent } from "@/test-utils";
import { WeddingMonthlyChart } from "@/features/dashboard/components/WeddingMonthlyChart";
import { createMockWedding } from "@/test-data";
import { server } from "@/mocks/server";
import { http, HttpResponse } from "msw";

describe("WeddingMonthlyChart", () => {
  it("shows empty state when no weddings in selected year", () => {
    render(
      <WeddingMonthlyChart
        weddings={[]}
        selectedYear={2025}
        onYearChange={vi.fn()}
      />,
    );

    expect(
      screen.getByText(/nenhum casamento agendado para 2025/i),
    ).toBeInTheDocument();
  });

  it("shows empty state for year with no matches", () => {
    render(
      <WeddingMonthlyChart
        weddings={[createMockWedding({ date: "2024-06-15" })]}
        selectedYear={2025}
        onYearChange={vi.fn()}
      />,
    );

    expect(
      screen.getByText(/nenhum casamento agendado para 2025/i),
    ).toBeInTheDocument();
  });

  it("renders chart container when data exists", () => {
    render(
      <WeddingMonthlyChart
        weddings={[createMockWedding({ date: "2025-06-15" })]}
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
        HttpResponse.json({ items: [], count: 0, limit: 1000, offset: 0 }),
      ),
    );

    render(
      <WeddingMonthlyChart
        weddings={[]}
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

  it("switches to Tarefas tab and shows expected content", async () => {
    const user = userEvent.setup();
    server.use(
      http.get("*/api/v1/scheduler/tasks/", () =>
        HttpResponse.json({ items: [], count: 0, limit: 1000, offset: 0 }),
      ),
    );

    render(
      <WeddingMonthlyChart
        weddings={[]}
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

  it("calls onYearChange when navigation buttons are clicked", async () => {
    const user = userEvent.setup();
    const onYearChange = vi.fn();
    render(
      <WeddingMonthlyChart
        weddings={[]}
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
