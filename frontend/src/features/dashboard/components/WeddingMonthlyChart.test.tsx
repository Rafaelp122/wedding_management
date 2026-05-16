import { describe, expect, it } from "vitest";
import { render, screen } from "@/test-utils";
import { WeddingMonthlyChart } from "@/features/dashboard/components/WeddingMonthlyChart";
import { createMockWedding } from "@/test-data";

describe("WeddingMonthlyChart", () => {
  it("shows empty state when no weddings in selected year", () => {
    render(
      <WeddingMonthlyChart
        weddings={[]}
        selectedYear={2025}
      />,
    );

    expect(
      screen.getByText(/nenhum casamento agendado para 2025/i),
    ).toBeInTheDocument();
  });

  it("shows empty state for year with no matches", () => {
    render(
      <WeddingMonthlyChart
        weddings={[createMockWedding({ date: "2024-06-15" })]}
        selectedYear={2025}
      />,
    );

    expect(
      screen.getByText(/nenhum casamento agendado para 2025/i),
    ).toBeInTheDocument();
  });

  it("renders chart container when data exists", () => {
    render(
      <WeddingMonthlyChart
        weddings={[createMockWedding({ date: "2025-06-15" })]}
        selectedYear={2025}
      />,
    );

    expect(screen.getByText("Casamentos por Mês")).toBeInTheDocument();
    expect(
      screen.getByText(/Distribuição de casamentos ao longo de 2025/),
    ).toBeInTheDocument();
  });
});
