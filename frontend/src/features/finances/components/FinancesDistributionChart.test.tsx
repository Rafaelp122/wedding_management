import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@/test-utils";
import { WeddingFinancesDistributionChart } from "./FinancesDistributionChart";
import { createMockBudgetCategory } from "@/test-data";

// ---------------------------------------------------------------------------
// Mock Recharts so it renders predictable DOM in jsdom (where container
// dimensions are 0 and Recharts' ResponsiveContainer would skip rendering).
// ---------------------------------------------------------------------------
vi.mock("recharts", () => ({
  ResponsiveContainer: ({
    children,
    width,
    height,
  }: {
    children: React.ReactNode;
    width?: string | number;
    height?: string | number;
  }) => <div data-testid="recharts-container" style={{ width, height }}>{children}</div>,
  BarChart: ({
    children,
    data,
  }: {
    children: React.ReactNode;
    data: unknown[];
  }) => <div data-testid="bar-chart" data-items={data.length}>{children}</div>,
  Bar: ({ dataKey, name }: { dataKey: string; name?: string }) => (
    <div data-testid={`bar-${dataKey}`}>{name}</div>
  ),
  CartesianGrid: () => <div data-testid="cartesian-grid" />,
  XAxis: ({ dataKey }: { dataKey: string }) => (
    <div data-testid="x-axis" data-datakey={dataKey} />
  ),
  YAxis: () => <div data-testid="y-axis" />,
  Tooltip: () => <div data-testid="tooltip" />,
  Legend: () => <div data-testid="legend" />,
}));

describe("WeddingFinancesDistributionChart", () => {
  // -----------------------------------------------------------------------
  // 1. Renders chart with given categories
  // -----------------------------------------------------------------------
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

    // Card elements
    expect(screen.getByText("Distribuição por Categoria")).toBeInTheDocument();
    expect(
      screen.getByText(
        "Comparativo entre valores estimados e gastos reais",
      ),
    ).toBeInTheDocument();

    // Chart container rendered
    expect(screen.getByTestId("recharts-container")).toBeInTheDocument();
    expect(screen.getByTestId("bar-chart")).toBeInTheDocument();

    // Bar chart receives the correct number of data items
    expect(
      screen.getByTestId("bar-chart").getAttribute("data-items"),
    ).toBe("2");

    // Legend labels
    expect(screen.getByTestId("bar-estimado")).toHaveTextContent("Estimado");
    expect(screen.getByTestId("bar-real")).toHaveTextContent("Realizado");
  });

  // -----------------------------------------------------------------------
  // 2. Renders with empty categories without crashing
  // -----------------------------------------------------------------------
  it("renders with empty categories without crashing", () => {
    render(<WeddingFinancesDistributionChart categories={[]} />);

    // Card elements still render
    expect(screen.getByText("Distribuição por Categoria")).toBeInTheDocument();
    expect(
      screen.getByText(
        "Comparativo entre valores estimados e gastos reais",
      ),
    ).toBeInTheDocument();

    // Chart container still renders
    expect(screen.getByTestId("recharts-container")).toBeInTheDocument();
    expect(screen.getByTestId("bar-chart")).toBeInTheDocument();

    // No data items
    expect(
      screen.getByTestId("bar-chart").getAttribute("data-items"),
    ).toBe("0");
  });
});
