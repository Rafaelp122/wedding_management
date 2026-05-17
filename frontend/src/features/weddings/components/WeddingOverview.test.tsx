/* eslint-disable @typescript-eslint/no-explicit-any */
import { describe, expect, it, vi, beforeEach } from "vitest";
import { render, screen } from "@/test-utils";
import { WeddingOverview } from "@/features/weddings/components/WeddingOverview";
import { createMockWedding } from "@/test-data";
import type { WeddingDashboardOut } from "@/api/generated/v1/models/weddingDashboardOut";

vi.mock("@/api/generated/v1/endpoints/dashboard/dashboard", () => ({
  useDashboardWedding: vi.fn(),
}));

import { useDashboardWedding } from "@/api/generated/v1/endpoints/dashboard/dashboard";

const emptyDashboard: WeddingDashboardOut = {
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
  beforeEach(() => {
    vi.mocked(useDashboardWedding).mockReturnValue({
      data: { data: emptyDashboard },
      isLoading: false,
    } as any);
  });

  it("renders couple names", () => {
    render(<WeddingOverview wedding={mockWedding} />);

    expect(screen.getByText("João & Maria")).toBeInTheDocument();
  });

  it("renders formatted date and location", () => {
    render(<WeddingOverview wedding={mockWedding} />);

    // The date is formatted with Intl.DateTimeFormat("pt-BR")
    // "2025-06-15" with month:"long" should produce "15 de junho de 2025"
    expect(screen.getByText(/15\s+de\s+junho/i)).toBeInTheDocument();
    // Location should appear in the same paragraph
    expect(screen.getByText(/São Paulo/)).toBeInTheDocument();
  });

  it("renders status badge with correct label", () => {
    render(<WeddingOverview wedding={mockWedding} />);

    expect(screen.getByText("Em Andamento")).toBeInTheDocument();
  });

  it("renders status badge for COMPLETED status", () => {
    render(
      <WeddingOverview
        wedding={createMockWedding({ status: "COMPLETED" })}
      />,
    );

    expect(screen.getByText("Concluído")).toBeInTheDocument();
  });

  it("renders 4 metric cards with dashboard data", () => {
    const dashboardData: WeddingDashboardOut = {
      days_until_wedding: 45,
      budget_percentage_used: 62,
      tasks_completed: 7,
      tasks_total: 20,
      contracts_signed: 3,
      contracts_total: 8,
      upcoming_installments: [],
      urgent_tasks: [],
      categories_summary: [],
    };

    vi.mocked(useDashboardWedding).mockReturnValue({
      data: { data: dashboardData },
      isLoading: false,
    } as any);

    render(<WeddingOverview wedding={mockWedding} />);

    // Countdown card
    expect(screen.getByText("Contagem Regressiva")).toBeInTheDocument();
    expect(screen.getByText("45")).toBeInTheDocument();

    // Financial health card
    expect(screen.getByText("Saúde Financeira")).toBeInTheDocument();
    expect(screen.getByText("62%")).toBeInTheDocument();

    // Tasks card
    expect(screen.getByText("Tarefas Concluídas")).toBeInTheDocument();
    expect(screen.getByText("7/20")).toBeInTheDocument();

    // Contracts card
    expect(screen.getByText("Contratos")).toBeInTheDocument();
    expect(screen.getByText("3/8")).toBeInTheDocument();
  });

  it("shows fallback values when dashboard data is missing", () => {
    vi.mocked(useDashboardWedding).mockReturnValue({
      data: undefined,
      isLoading: false,
    } as any);

    render(<WeddingOverview wedding={mockWedding} />);

    // Should show dash/zero fallbacks
    expect(screen.getByText("—")).toBeInTheDocument();
    expect(screen.getByText("0%")).toBeInTheDocument();
    // Both tasks and contracts show "0/0" when no data
    const zeroOverZero = screen.getAllByText("0/0");
    expect(zeroOverZero).toHaveLength(2);
  });

  it("shows empty states when no urgent tasks or upcoming installments", () => {
    render(<WeddingOverview wedding={mockWedding} />);

    expect(screen.getByText("Ações Necessárias")).toBeInTheDocument();
    expect(screen.getByText("Tudo em dia por aqui!")).toBeInTheDocument();
    expect(screen.getByText("Próximos Vencimentos")).toBeInTheDocument();
    expect(screen.getByText("Nenhum pagamento próximo.")).toBeInTheDocument();
  });

  it("shows urgent tasks when present", () => {
    const dashboardWithTasks: WeddingDashboardOut = {
      ...emptyDashboard,
      urgent_tasks: [
        { uuid: "t-1", title: "Fechar buffet", due_date: "2025-04-01" },
        { uuid: "t-2", title: "Confirmar igreja", due_date: "2025-04-15" },
      ],
    };

    vi.mocked(useDashboardWedding).mockReturnValue({
      data: { data: dashboardWithTasks },
      isLoading: false,
    } as any);

    render(<WeddingOverview wedding={mockWedding} />);

    expect(screen.getByText("Fechar buffet")).toBeInTheDocument();
    expect(screen.getByText("Confirmar igreja")).toBeInTheDocument();
    // Empty state text should NOT be present
    expect(
      screen.queryByText("Tudo em dia por aqui!"),
    ).not.toBeInTheDocument();
    const priorities = screen.getAllByText("Prioridade: Alta");
    expect(priorities).toHaveLength(2);
  });

  it("shows upcoming installments when present", () => {
    const dashboardWithInstallments: WeddingDashboardOut = {
      ...emptyDashboard,
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
    };

    vi.mocked(useDashboardWedding).mockReturnValue({
      data: { data: dashboardWithInstallments },
      isLoading: false,
    } as any);

    render(<WeddingOverview wedding={mockWedding} />);

    expect(screen.getByText("Parcela #3")).toBeInTheDocument();
    expect(screen.getByText("Parcela #1")).toBeInTheDocument();
    // Empty state text should NOT be present
    expect(
      screen.queryByText("Nenhum pagamento próximo."),
    ).not.toBeInTheDocument();

    // Should show overdue status
    expect(screen.getByText("Atrasado")).toBeInTheDocument();
    expect(screen.getByText("Pendente")).toBeInTheDocument();
  });

  it("renders view planning and view finances links", () => {
    render(<WeddingOverview wedding={mockWedding} />);

    expect(
      screen.getByRole("link", { name: /ver planejamento/i }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("link", { name: /ver finanças/i }),
    ).toBeInTheDocument();
  });

  it("has correct link URLs", () => {
    render(<WeddingOverview wedding={mockWedding} />);

    const planningLink = screen.getByRole("link", {
      name: /ver planejamento/i,
    });
    expect(planningLink).toHaveAttribute(
      "href",
      "/weddings/w-1?tab=planning&subtab=checklist",
    );

    const financesLink = screen.getByRole("link", {
      name: /ver finanças/i,
    });
    expect(financesLink).toHaveAttribute(
      "href",
      "/weddings/w-1?tab=finances",
    );
  });
});
