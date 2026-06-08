import { describe, expect, it } from "vitest";
import { render, screen } from "@/test-utils";
import { StatsCards } from "@/features/dashboard/components/StatsCards";
import { createMockDashboardSummary } from "@/test-data";

describe("StatsCards", () => {
  it("renders all 4 stat cards", () => {
    render(
      <StatsCards summary={createMockDashboardSummary()} />,
    );

    expect(screen.getByText("Parcelas Vencidas")).toBeInTheDocument();
    expect(screen.getByText("Contratos Pendentes")).toBeInTheDocument();
    expect(screen.getByText(/Parcelas a Vencer/i)).toBeInTheDocument();
    expect(screen.getByText("Tarefas Atrasadas")).toBeInTheDocument();
  });

  it("shows zero values when summary is undefined", () => {
    render(<StatsCards summary={undefined} />);

    const zeros = screen.getAllByText("0");
    expect(zeros.length).toBeGreaterThanOrEqual(2);
  });

  it("renders summary values", () => {
    render(
      <StatsCards
        summary={createMockDashboardSummary({
          urgent_tasks_count: 3,
          overdue_installments_amount: "12350.00",
          overdue_installments_count: 2,
          pending_contracts_count: 5,
        })}
      />,
    );

    // Urgent tasks (Card 3)
    expect(screen.getByText("3")).toBeInTheDocument();
    expect(screen.getByText("Ação Necessária: 3 pendências")).toBeInTheDocument();

    // Overdue payments (Card 2)
    expect(screen.getByText("R$ 12.350,00")).toBeInTheDocument();
    expect(screen.getByText("Ação Necessária: 2 pendências")).toBeInTheDocument();

    // Pending contracts (Card 4)
    expect(screen.getByText("5")).toBeInTheDocument();
    expect(screen.getByText("Aguardando assinatura/sinal")).toBeInTheDocument();
  });
});
