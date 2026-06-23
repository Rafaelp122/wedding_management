import { describe, expect, it } from "vitest";
import { render, screen, userEvent } from "@/test-utils";
import { WeddingStatsCards } from "@/features/dashboard/components/WeddingStatsCards";
import {
  createMockWeddingDashboard,
  createMockWeddingDashboardInstallment,
  createMockWeddingDashboardTask,
} from "@/test-data";

describe("WeddingStatsCards", () => {
  it("renders four skeleton placeholders when loading", () => {
    const { container } = render(<WeddingStatsCards isLoading />);
    const skeletons = container.querySelectorAll(".animate-pulse");
    expect(skeletons.length).toBe(4);
  });

  it("renders days until wedding card with normal styling", () => {
    render(
      <WeddingStatsCards
        data={createMockWeddingDashboard({ days_until_wedding: 120 })}
      />,
    );
    expect(screen.getByText("120")).toBeInTheDocument();
    expect(screen.getByText(/120 dias restantes/)).toBeInTheDocument();
  });

  it("shows 'Hoje!' when days until wedding is 0", () => {
    render(
      <WeddingStatsCards
        data={createMockWeddingDashboard({ days_until_wedding: 0 })}
      />,
    );
    expect(screen.getByText("Hoje!")).toBeInTheDocument();
  });

  it("shows urgent styling when 30 days or fewer remain", () => {
    render(
      <WeddingStatsCards
        data={createMockWeddingDashboard({ days_until_wedding: 15 })}
      />,
    );
    expect(screen.getByText("15")).toBeInTheDocument();
    expect(
      screen.getByText(/Urgente — menos de 30 dias/),
    ).toBeInTheDocument();
  });

  it("shows warning styling when between 31 and 90 days remain", () => {
    render(
      <WeddingStatsCards
        data={createMockWeddingDashboard({ days_until_wedding: 60 })}
      />,
    );
    expect(screen.getByText("60")).toBeInTheDocument();
    expect(screen.getByText(/Menos de 90 dias/)).toBeInTheDocument();
  });

  it("renders budget used card with progress bar", () => {
    render(
      <WeddingStatsCards
        data={createMockWeddingDashboard({ budget_percentage_used: 45.5 })}
      />,
    );
    expect(screen.getByText("45.5%")).toBeInTheDocument();
    expect(screen.getByText("Dentro do orçamento")).toBeInTheDocument();
  });

  it("shows critical budget styling at or above 90%", () => {
    render(
      <WeddingStatsCards
        data={createMockWeddingDashboard({ budget_percentage_used: 92 })}
      />,
    );
    expect(screen.getByText("92.0%")).toBeInTheDocument();
    expect(screen.getByText("Limite crítico")).toBeInTheDocument();
  });

  it("shows warning budget styling between 75% and 90%", () => {
    render(
      <WeddingStatsCards
        data={createMockWeddingDashboard({ budget_percentage_used: 80 })}
      />,
    );
    expect(screen.getByText("80.0%")).toBeInTheDocument();
    expect(screen.getByText("Atenção ao budget")).toBeInTheDocument();
  });

  it("renders tasks completed card with progress", () => {
    render(
      <WeddingStatsCards
        data={createMockWeddingDashboard({
          tasks_completed: 8,
          tasks_total: 20,
        })}
      />,
    );
    expect(screen.getByText("8")).toBeInTheDocument();
    expect(screen.getByText("/ 20")).toBeInTheDocument();
    expect(screen.getByText("12 pendentes")).toBeInTheDocument();
  });

  it("shows success state when all tasks are completed", () => {
    render(
      <WeddingStatsCards
        data={createMockWeddingDashboard({
          tasks_completed: 5,
          tasks_total: 5,
        })}
      />,
    );
    expect(screen.getByText(/Todas concluídas/)).toBeInTheDocument();
  });

  it("renders contracts card with progress", () => {
    render(
      <WeddingStatsCards
        data={createMockWeddingDashboard({
          contracts_signed: 3,
          contracts_total: 5,
        })}
      />,
    );
    expect(screen.getByText("3")).toBeInTheDocument();
    expect(screen.getByText("/ 5")).toBeInTheDocument();
    expect(
      screen.getByText(/2 pendentes de assinatura/),
    ).toBeInTheDocument();
  });

  it("shows all signed when all contracts are signed", () => {
    render(
      <WeddingStatsCards
        data={createMockWeddingDashboard({
          contracts_signed: 3,
          contracts_total: 3,
        })}
      />,
    );
    expect(screen.getByText(/Todos assinados/)).toBeInTheDocument();
  });

  it("shows 'Nenhum contrato' when contracts_total is 0", () => {
    render(
      <WeddingStatsCards
        data={createMockWeddingDashboard({
          contracts_signed: 0,
          contracts_total: 0,
        })}
      />,
    );
    expect(screen.getByText("Nenhum contrato")).toBeInTheDocument();
  });

  it("renders 'Ver Parcelas' button when upcoming installments exist", () => {
    render(
      <WeddingStatsCards
        data={createMockWeddingDashboard({
          upcoming_installments: [createMockWeddingDashboardInstallment()],
        })}
      />,
    );
    expect(screen.getByText("Ver Parcelas")).toBeInTheDocument();
  });

  it("does not render 'Ver Parcelas' when no upcoming installments", () => {
    render(
      <WeddingStatsCards
        data={createMockWeddingDashboard({ upcoming_installments: [] })}
      />,
    );
    expect(screen.queryByText("Ver Parcelas")).not.toBeInTheDocument();
  });

  it("renders 'Ver Urgentes' button when urgent tasks exist", () => {
    render(
      <WeddingStatsCards
        data={createMockWeddingDashboard({
          urgent_tasks: [createMockWeddingDashboardTask()],
        })}
      />,
    );
    expect(screen.getByText("Ver Urgentes")).toBeInTheDocument();
  });

  it("does not render 'Ver Urgentes' when no urgent tasks", () => {
    render(
      <WeddingStatsCards
        data={createMockWeddingDashboard({ urgent_tasks: [] })}
      />,
    );
    expect(screen.queryByText("Ver Urgentes")).not.toBeInTheDocument();
  });

  it("opens installment sheet and renders installment details", async () => {
    const user = userEvent.setup();
    render(
      <WeddingStatsCards
        data={createMockWeddingDashboard({
          upcoming_installments: [
            createMockWeddingDashboardInstallment({
              uuid: "inst-1",
              installment_number: 2,
              amount: "750.00",
              status: "PENDING",
            }),
          ],
        })}
      />,
    );

    await user.click(screen.getByText("Ver Parcelas"));

    expect(screen.getByText("Próximas Parcelas")).toBeInTheDocument();
    expect(screen.getByText("Parcela #2")).toBeInTheDocument();
    expect(screen.getByText("750,00")).toBeInTheDocument();
  });

  it("opens urgent tasks sheet and renders task details", async () => {
    const user = userEvent.setup();
    render(
      <WeddingStatsCards
        data={createMockWeddingDashboard({
          urgent_tasks: [
            createMockWeddingDashboardTask({
              uuid: "t-1",
              title: "Finalizar decoração",
              due_date: "2026-01-15",
            }),
          ],
        })}
      />,
    );

    await user.click(screen.getByText("Ver Urgentes"));

    expect(screen.getByText("Tarefas Urgentes")).toBeInTheDocument();
    expect(screen.getByText("Finalizar decoração")).toBeInTheDocument();
  });

  it("shows overdue styling in installment sheet for OVERDUE items", async () => {
    const user = userEvent.setup();
    const pastDate = new Date();
    pastDate.setDate(pastDate.getDate() - 4);
    render(
      <WeddingStatsCards
        data={createMockWeddingDashboard({
          upcoming_installments: [
            createMockWeddingDashboardInstallment({
              uuid: "inst-overdue",
              installment_number: 1,
              amount: "1200.00",
              due_date: pastDate.toISOString().slice(0, 10),
              status: "OVERDUE",
            }),
          ],
        })}
      />,
    );

    await user.click(screen.getByText("Ver Parcelas"));

    expect(screen.getByText("Em atraso")).toBeInTheDocument();
    expect(screen.getByText("1.200,00")).toBeInTheDocument();
  });

  it("shows default zero values when data is undefined", () => {
    render(<WeddingStatsCards data={undefined} />);
    expect(screen.getByText("Hoje!")).toBeInTheDocument();
    expect(screen.getByText("0.0%")).toBeInTheDocument();
  });
});
