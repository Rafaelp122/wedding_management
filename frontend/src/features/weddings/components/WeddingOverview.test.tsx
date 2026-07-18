import { describe, expect, it, vi } from "vitest";
import { render, screen, userEvent } from "@/test-utils";
import { WeddingOverview } from "@/features/weddings/components/WeddingOverview";
import { createMockWedding } from "@/test-data";
import type { WeddingDashboardOut } from "@/api/generated/v1/models/weddingDashboardOut";

const emptyOverview: WeddingDashboardOut = {
  days_until_wedding: 120,
  budget_percentage_used: 35,
  tasks_completed: 3,
  tasks_total: 10,
  contracts_signed: 2,
  contracts_total: 4,
  upcoming_installments: [],
  urgent_tasks: [],
  categories_summary: [],
};

const mockWedding = createMockWedding({
  groom_name: "João",
  bride_name: "Maria",
  date: "2025-06-15",
  location: "São Paulo",
});

describe("WeddingOverview", () => {
  it("renders couple names", () => {
    render(<WeddingOverview wedding={mockWedding} overview={null} />);

    expect(screen.getByText("João & Maria")).toBeInTheDocument();
  });

  it("renders formatted date and location", () => {
    render(<WeddingOverview wedding={mockWedding} overview={null} />);



    expect(screen.getByText(/15\s+de\s+junho/i)).toBeInTheDocument();

    expect(screen.getByText(/São Paulo/)).toBeInTheDocument();
  });

  it("renders status badge with correct label", () => {
    render(<WeddingOverview wedding={mockWedding} overview={null} />);

    expect(screen.getByText("Em Andamento")).toBeInTheDocument();
  });

  it("renders status badge for COMPLETED status", () => {
    render(
      <WeddingOverview
        wedding={createMockWedding({ status: "COMPLETED" })}
        overview={null}
      />,
    );

    expect(screen.getByText("Concluído")).toBeInTheDocument();
  });

  it("renders 4 metric cards with dashboard data", () => {
    render(
      <WeddingOverview
        wedding={mockWedding}
        overview={{
          days_until_wedding: 45,
          budget_percentage_used: 62,
          tasks_completed: 7,
          tasks_total: 20,
          contracts_signed: 3,
          contracts_total: 8,
          upcoming_installments: [],
          urgent_tasks: [],
          categories_summary: [],
        }}
      />,
    );


    expect(screen.getByText("Contagem Regressiva")).toBeInTheDocument();
    expect(screen.getByText("45")).toBeInTheDocument();


    expect(screen.getByText("Saúde Financeira")).toBeInTheDocument();
    expect(screen.getByText("62%")).toBeInTheDocument();


    expect(screen.getByText("Tarefas Concluídas")).toBeInTheDocument();
    expect(screen.getByText("7/20")).toBeInTheDocument();


    expect(screen.getByText("Contratos")).toBeInTheDocument();
    expect(screen.getByText("3/8")).toBeInTheDocument();
  });

  it("shows fallback values when dashboard data is missing", () => {
    render(<WeddingOverview wedding={mockWedding} overview={null} />);


    expect(screen.getByText("—")).toBeInTheDocument();
    expect(screen.getByText("0%")).toBeInTheDocument();

    const zeroOverZero = screen.getAllByText("0/0");
    expect(zeroOverZero).toHaveLength(2);
  });

  it("shows empty states when no urgent tasks or upcoming installments", () => {
    render(<WeddingOverview wedding={mockWedding} overview={emptyOverview} />);

    expect(screen.getByText("Ações Necessárias")).toBeInTheDocument();
    expect(screen.getByText("Tudo em dia por aqui!")).toBeInTheDocument();
    expect(screen.getByText("Próximos Vencimentos")).toBeInTheDocument();
    expect(screen.getByText("Nenhum pagamento próximo.")).toBeInTheDocument();
  });

  it("shows urgent tasks when present", () => {
    render(
      <WeddingOverview
        wedding={mockWedding}
        overview={{
          ...emptyOverview,
          urgent_tasks: [
            { uuid: "t-1", title: "Fechar buffet", due_date: "2025-04-01" },
            { uuid: "t-2", title: "Confirmar igreja", due_date: "2025-04-15" },
          ],
        }}
      />,
    );

    expect(screen.getByText("Fechar buffet")).toBeInTheDocument();
    expect(screen.getByText("Confirmar igreja")).toBeInTheDocument();

    expect(
      screen.queryByText("Tudo em dia por aqui!"),
    ).not.toBeInTheDocument();
    const priorities = screen.getAllByText("Prioridade: Alta");
    expect(priorities).toHaveLength(2);
  });

  it("shows upcoming installments when present", () => {
    render(
      <WeddingOverview
        wedding={mockWedding}
        overview={{
          ...emptyOverview,
          upcoming_installments: [
            {
              uuid: "inst-1",
              installment_number: 3,
              amount: "1500.00",
              due_date: "2025-05-10",
              status: "PENDING",
            },
            {
              uuid: "inst-2",
              installment_number: 1,
              amount: "2000.00",
              due_date: "2025-04-20",
              status: "OVERDUE",
            },
          ],
        }}
      />,
    );

    expect(screen.getByText("Parcela #3")).toBeInTheDocument();
    expect(screen.getByText("Parcela #1")).toBeInTheDocument();

    expect(
      screen.queryByText("Nenhum pagamento próximo."),
    ).not.toBeInTheDocument();


    expect(screen.getByText("Atrasado")).toBeInTheDocument();
    expect(screen.getByText("Pendente")).toBeInTheDocument();
  });

  it("renders view planning and view finances buttons and calls callbacks when clicked", async () => {
    const onNavigateToPlanning = vi.fn();
    const onNavigateToFinances = vi.fn();

    render(
      <WeddingOverview
        wedding={mockWedding}
        overview={null}
        onNavigateToPlanning={onNavigateToPlanning}
        onNavigateToFinances={onNavigateToFinances}
      />,
    );

    const planningBtn = screen.getByRole("button", { name: /ver planejamento/i });
    const financesBtn = screen.getByRole("button", { name: /ver finanças/i });

    expect(planningBtn).toBeInTheDocument();
    expect(financesBtn).toBeInTheDocument();

    await userEvent.click(planningBtn);
    expect(onNavigateToPlanning).toHaveBeenCalledTimes(1);

    await userEvent.click(financesBtn);
    expect(onNavigateToFinances).toHaveBeenCalledTimes(1);
  });
});
