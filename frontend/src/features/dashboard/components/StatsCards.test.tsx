import { describe, expect, it } from "vitest";
import { render, screen } from "@/test-utils";
import { StatsCards } from "@/features/dashboard/components/StatsCards";
import { createMockDashboardSummary } from "@/test-data";

describe("StatsCards", () => {
  it("renders all 4 stat cards", () => {
    render(
      <StatsCards summary={createMockDashboardSummary()} />,
    );

    expect(screen.getByText("Casamentos Ativos")).toBeInTheDocument();
    expect(screen.getByText("Casamentos este Mês")).toBeInTheDocument();
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
          active_weddings: 8,
          urgent_tasks_count: 3,
        })}
      />,
    );

    expect(screen.getByText("8")).toBeInTheDocument();
    expect(screen.getByText("3")).toBeInTheDocument();
  });
});
