import { describe, expect, it } from "vitest";
import { render, screen, waitFor, userEvent } from "@/test-utils";
import { StatsCards } from "@/features/dashboard/components/StatsCards";
import {
  createMockDashboardSummary,
  createMockDashboardInstallmentDetail,
  createMockDashboardTaskDetail,
  createMockDashboardContractDetail,
} from "@/test-data";

describe("StatsCards", () => {
  it("renders all 4 stat cards", () => {
    render(<StatsCards summary={createMockDashboardSummary()} />);

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

    expect(screen.getByText("3")).toBeInTheDocument();
    expect(screen.getByText("Ação Necessária: 3 pendências")).toBeInTheDocument();
    expect(screen.getByText("12.350,00")).toBeInTheDocument();
    expect(screen.getByText("Ação Necessária: 2 pendências")).toBeInTheDocument();
    expect(screen.getByText("5")).toBeInTheDocument();
    expect(screen.getByText("Aguardando assinatura/sinal")).toBeInTheDocument();
  });

  it("opens overdue installments Sheet and renders content", async () => {
    const user = userEvent.setup();

    render(
      <StatsCards
        summary={createMockDashboardSummary({
          overdue_installments_count: 1,
          overdue_installments_amount: "5000.00",
          pending_installments_7d: "0",
          overdue_installments: [
            createMockDashboardInstallmentDetail({
              uuid: "inst-1",
              installment_number: 1,
              amount: "5000.00",
              due_date: "2025-01-15",
              wedding_name: "Ana e Carlos",
            }),
          ],
        })}
      />,
    );

    const openButton = screen.getByRole("button", { name: "Ver Parcelas" });
    await user.click(openButton);

    await waitFor(() => {
      const headers = screen.getAllByText("Parcelas Vencidas");
      expect(headers.length).toBeGreaterThanOrEqual(2);
      const amounts = screen.getAllByText("5.000,00");
      expect(amounts.length).toBeGreaterThanOrEqual(1);
      expect(screen.getByText(/Ana e Carlos/)).toBeInTheDocument();
    });
  });

  it("opens urgent tasks Sheet and renders content", async () => {
    const user = userEvent.setup();

    render(
      <StatsCards
        summary={createMockDashboardSummary({
          urgent_tasks_count: 1,
          urgent_tasks: [
            createMockDashboardTaskDetail({
              uuid: "task-1",
              title: "Contratar buffet",
              due_date: "2025-01-01",
              wedding_name: "Ana e Carlos",
            }),
          ],
        })}
      />,
    );

    const taskButtons = screen.getAllByRole("button", { name: "Ver Tarefas" });
    await user.click(taskButtons[0]);

    await waitFor(() => {
      expect(screen.getByText("Contratar buffet")).toBeInTheDocument();
      expect(screen.getByText(/Ana e Carlos/)).toBeInTheDocument();
    });
  });

  it("opens pending installments Sheet and renders content", async () => {
    const user = userEvent.setup();

    render(
      <StatsCards
        summary={createMockDashboardSummary({
          pending_installments_7d: "750.00",
          overdue_installments_count: 0,
          overdue_installments_amount: "0",
          upcoming_installments: [
            createMockDashboardInstallmentDetail({
              uuid: "inst-p1",
              installment_number: 1,
              amount: "750.00",
              due_date: "2025-06-20",
              status: "PENDING",
              wedding_name: "Ana e Carlos",
            }),
          ],
        })}
      />,
    );

    await user.click(screen.getByRole("button", { name: "Ver Parcelas" }));

    await waitFor(() => {
      const matches = screen.getAllByText("750,00");
      expect(matches.length).toBeGreaterThanOrEqual(2);
      expect(screen.getByText(/Ana e Carlos/)).toBeInTheDocument();
    });
  });

  it("shows empty message in overdue Sheet when no data", async () => {
    const user = userEvent.setup();

    render(
      <StatsCards
        summary={createMockDashboardSummary({
          pending_installments_7d: "0",
          overdue_installments_count: 1,
          overdue_installments_amount: "100.00",
          overdue_installments: [],
        })}
      />,
    );

    await user.click(screen.getByRole("button", { name: "Ver Parcelas" }));

    await waitFor(() => {
      expect(screen.getByText("Nenhuma parcela vencida.")).toBeInTheDocument();
    });
  });

  it("opens pending contracts Sheet and renders content", async () => {
    const user = userEvent.setup();

    render(
      <StatsCards
        summary={createMockDashboardSummary({
          pending_contracts_count: 1,
          pending_contracts: [
            createMockDashboardContractDetail({
              uuid: "ctr-1",
              supplier_name: "Buffet Sabor",
              total_amount: "15000.00",
              wedding_name: "Ana e Carlos",
            }),
          ],
        })}
      />,
    );

    const openButton = screen.getByRole("button", { name: "Ver Contratos" });
    await user.click(openButton);

    await waitFor(() => {
      expect(screen.getByText("Buffet Sabor")).toBeInTheDocument();
      expect(screen.getByText("15.000,00")).toBeInTheDocument();
      expect(screen.getByText(/Ana e Carlos/)).toBeInTheDocument();
    });
  });
});
