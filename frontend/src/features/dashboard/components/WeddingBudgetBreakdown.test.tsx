import { describe, expect, it } from "vitest";
import { render, screen } from "@/test-utils";
import { WeddingBudgetBreakdown } from "@/features/dashboard/components/WeddingBudgetBreakdown";
import { createMockWeddingDashboardCategory } from "@/test-data";

describe("WeddingBudgetBreakdown", () => {
  it("renders skeleton placeholders when loading", () => {
    render(<WeddingBudgetBreakdown categories={[]} isLoading />);
    expect(
      screen.getByText("Orçamento por Categoria"),
    ).toBeInTheDocument();
  });

  it("renders empty state when categories is empty", () => {
    render(<WeddingBudgetBreakdown categories={[]} />);
    expect(
      screen.getByText("Nenhuma categoria de orçamento cadastrada."),
    ).toBeInTheDocument();
  });

  it("renders empty state when categories is undefined", () => {
    render(
      <WeddingBudgetBreakdown
        categories={undefined as unknown as []}
      />,
    );
    expect(
      screen.getByText("Nenhuma categoria de orçamento cadastrada."),
    ).toBeInTheDocument();
  });

  it("renders a single category with correct values", () => {
    render(
      <WeddingBudgetBreakdown
        categories={[
          createMockWeddingDashboardCategory({
            name: "Buffet",
            allocated: "10000.00",
            spent: "5000.00",
            percentage: 50,
          }),
        ]}
      />,
    );
    expect(screen.getByText("Buffet")).toBeInTheDocument();
    expect(screen.getByText("50%")).toBeInTheDocument();
    expect(screen.getByText("5.000,00")).toBeInTheDocument();
    expect(screen.getByText("10.000,00")).toBeInTheDocument();
  });

  it("renders multiple categories sorted by percentage descending", () => {
    render(
      <WeddingBudgetBreakdown
        categories={[
          createMockWeddingDashboardCategory({
            name: "Foto",
            allocated: "3000.00",
            spent: "1500.00",
            percentage: 50,
          }),
          createMockWeddingDashboardCategory({
            name: "Buffet",
            allocated: "10000.00",
            spent: "9000.00",
            percentage: 90,
          }),
          createMockWeddingDashboardCategory({
            name: "Decoração",
            allocated: "5000.00",
            spent: "3500.00",
            percentage: 70,
          }),
        ]}
      />,
    );

    const names = screen.getAllByText(/Buffet|Decoração|Foto/);
    expect(names).toHaveLength(3);
    expect(names[0]).toHaveTextContent("Buffet");
    expect(names[1]).toHaveTextContent("Decoração");
    expect(names[2]).toHaveTextContent("Foto");
  });

  it("shows danger styling when percentage is at or above 90%", () => {
    render(
      <WeddingBudgetBreakdown
        categories={[
          createMockWeddingDashboardCategory({
            name: "Buffet",
            allocated: "10000.00",
            spent: "9500.00",
            percentage: 95,
          }),
        ]}
      />,
    );
    expect(screen.getByText("95%").className).toContain("destructive");
  });

  it("shows warning styling when percentage is between 70% and 90%", () => {
    render(
      <WeddingBudgetBreakdown
        categories={[
          createMockWeddingDashboardCategory({
            name: "Decoração",
            allocated: "5000.00",
            spent: "3750.00",
            percentage: 75,
          }),
        ]}
      />,
    );
    const pct = screen.getByText("75%");
    expect(pct.className).toContain("amber");
  });

  it("shows over-budget display when percentage exceeds 100%", () => {
    render(
      <WeddingBudgetBreakdown
        categories={[
          createMockWeddingDashboardCategory({
            name: "Buffet",
            allocated: "10000.00",
            spent: "12000.00",
            percentage: 120,
          }),
        ]}
      />,
    );
    expect(screen.getByText("+20%")).toBeInTheDocument();
  });

  it("calculates and displays totals correctly", () => {
    render(
      <WeddingBudgetBreakdown
        categories={[
          createMockWeddingDashboardCategory({
            name: "Buffet",
            allocated: "10000.00",
            spent: "6000.00",
            percentage: 60,
          }),
          createMockWeddingDashboardCategory({
            name: "Foto",
            allocated: "5000.00",
            spent: "3000.00",
            percentage: 60,
          }),
        ]}
      />,
    );

    expect(screen.getByText("9.000,00")).toBeInTheDocument();
    expect(screen.getByText("15.000,00")).toBeInTheDocument();
    expect(screen.getByText("(60%)")).toBeInTheDocument();
  });

  it("shows danger total percentage when >= 90%", () => {
    render(
      <WeddingBudgetBreakdown
        categories={[
          createMockWeddingDashboardCategory({
            name: "Buffet",
            allocated: "10000.00",
            spent: "9500.00",
            percentage: 95,
          }),
        ]}
      />,
    );
    const totalPct = screen.getByText("(95%)");
    expect(totalPct.className).toContain("destructive");
  });

  it("shows warning total percentage when between 70% and 90%", () => {
    render(
      <WeddingBudgetBreakdown
        categories={[
          createMockWeddingDashboardCategory({
            name: "Buffet",
            allocated: "10000.00",
            spent: "7500.00",
            percentage: 75,
          }),
        ]}
      />,
    );
    const totalPct = screen.getByText("(75%)");
    expect(totalPct.className).toContain("amber");
  });

  it("shows success total percentage when below 70%", () => {
    render(
      <WeddingBudgetBreakdown
        categories={[
          createMockWeddingDashboardCategory({
            name: "Buffet",
            allocated: "10000.00",
            spent: "3000.00",
            percentage: 30,
          }),
        ]}
      />,
    );
    const totalPct = screen.getByText("(30%)");
    expect(totalPct.className).toContain("success");
  });
});
