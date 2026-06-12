import { describe, expect, it } from "vitest";
import { render, screen } from "@/test-utils";
import { WeddingFinancesDistributionChart } from "./FinancesDistributionChart";
import { createMockBudgetCategory } from "@/test-data";

describe("WeddingFinancesDistributionChart", () => {
  it("renders chart with given categories", () => {
    const categories = [
      createMockBudgetCategory({
        uuid: "bc-1",
        name: "Buffet",
        allocated_budget: "10000.00",
        total_spent: "7500.00",
      }),
      createMockBudgetCategory({
        uuid: "bc-2",
        name: "Decoração",
        allocated_budget: "5000.00",
        total_spent: "3200.00",
      }),
    ];

    render(<WeddingFinancesDistributionChart categories={categories} />);

    expect(screen.getByText("Distribuição por Categoria")).toBeInTheDocument();
    expect(
      screen.getByText(
        "Comparativo entre valores estimados e gastos reais",
      ),
    ).toBeInTheDocument();

    expect(screen.getByTestId("recharts-container")).toBeInTheDocument();
    expect(screen.getByTestId("bar-chart")).toBeInTheDocument();

    expect(
      screen.getByTestId("bar-chart").getAttribute("data-items"),
    ).toBe("2");

    expect(screen.getByTestId("bar-estimado")).toHaveTextContent("Estimado");
    expect(screen.getByTestId("bar-real")).toHaveTextContent("Realizado");
  });

  it("renders with empty categories without crashing", () => {
    render(<WeddingFinancesDistributionChart categories={[]} />);

    expect(screen.getByText("Distribuição por Categoria")).toBeInTheDocument();
    expect(
      screen.getByText(
        "Comparativo entre valores estimados e gastos reais",
      ),
    ).toBeInTheDocument();

    expect(screen.getByTestId("recharts-container")).toBeInTheDocument();
    expect(screen.getByTestId("bar-chart")).toBeInTheDocument();

    expect(
      screen.getByTestId("bar-chart").getAttribute("data-items"),
    ).toBe("0");
  });
});
