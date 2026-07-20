import { describe, expect, it, vi } from "vitest";
import { render, screen, userEvent } from "@/test-utils";
import { WeddingMonthlyChartView } from "./WeddingMonthlyChartView";

const baseProps = {
  selectedYear: 2026,
  onYearChange: vi.fn(),
  activeTab: "casamentos",
  onTabChange: vi.fn(),
  isLoadingInstallments: false,
  isLoadingTasks: false,
  monthlyData: [],
  hasData: false,
  cashFlowData: [],
  hasCashFlowData: false,
  tasksData: [],
  hasTasksData: false,
};

describe("WeddingMonthlyChartView", () => {
  it("renders weddings data and delegates navigation and tab changes", async () => {
    const user = userEvent.setup();
    const onYearChange = vi.fn();
    const onTabChange = vi.fn();
    render(
      <WeddingMonthlyChartView
        {...baseProps}
        onYearChange={onYearChange}
        onTabChange={onTabChange}
        monthlyData={[{ name: "Jan", casamentos: 2 }]}
        hasData
      />,
    );

    expect(screen.getByTestId("bar-casamentos")).toBeInTheDocument();
    await user.click(screen.getByLabelText("Ano anterior"));
    await user.click(screen.getByLabelText("Próximo ano"));
    await user.click(screen.getByRole("tab", { name: /financeiro/i }));

    expect(onYearChange).toHaveBeenNthCalledWith(1, 2025);
    expect(onYearChange).toHaveBeenNthCalledWith(2, 2027);
    expect(onTabChange).toHaveBeenCalledWith("financeiro");
  });

  it("renders the finance loading, data, and empty branches", () => {
    const { rerender } = render(
      <WeddingMonthlyChartView
        {...baseProps}
        activeTab="financeiro"
        isLoadingInstallments
      />,
    );
    expect(document.querySelectorAll("[class*='animate-pulse']")).toHaveLength(12);

    rerender(
      <WeddingMonthlyChartView
        {...baseProps}
        activeTab="financeiro"
        cashFlowData={[{ name: "Jan", pago: 1000, pendente: 500 }]}
        hasCashFlowData
      />,
    );
    expect(screen.getByTestId("bar-pago")).toBeInTheDocument();
    expect(screen.getByTestId("bar-pendente")).toBeInTheDocument();

    rerender(<WeddingMonthlyChartView {...baseProps} activeTab="financeiro" />);
    expect(screen.getByText(/nenhum compromisso financeiro para 2026/i)).toBeInTheDocument();
  });

  it("renders the tasks loading, data, and empty branches", () => {
    const { rerender } = render(
      <WeddingMonthlyChartView {...baseProps} activeTab="tarefas" isLoadingTasks />,
    );
    expect(document.querySelectorAll("[class*='animate-pulse']")).toHaveLength(8);

    rerender(
      <WeddingMonthlyChartView
        {...baseProps}
        activeTab="tarefas"
        tasksData={[{ name: "Casamento", concluido: 75 }]}
        hasTasksData
      />,
    );
    expect(screen.getByTestId("bar-concluido")).toBeInTheDocument();

    rerender(<WeddingMonthlyChartView {...baseProps} activeTab="tarefas" />);
    expect(screen.getByText(/nenhum casamento com tarefas em 2026/i)).toBeInTheDocument();
  });
});
