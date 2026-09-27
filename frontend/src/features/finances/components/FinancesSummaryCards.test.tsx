import { describe, expect, it } from "vitest";
import { render, screen } from "@/test-utils";
import { WeddingFinancesSummaryCards } from "@/features/finances/components/FinancesSummaryCards";
import { createMockBudget } from "@/test-data";

describe("WeddingFinancesSummaryCards", () => {
  it("renders budget and spent cards", () => {
    render(
      <WeddingFinancesSummaryCards totalEstimated={50000} totalSpent={25000} />,
    );

    expect(screen.getByText("Orçamento Total")).toBeInTheDocument();
    expect(screen.getByText("Total Gasto")).toBeInTheDocument();
    expect(screen.getByText("Saldo Disponível")).toBeInTheDocument();
  });

  it("shows 0% usage when totalEstimated is 0", () => {
    render(
      <WeddingFinancesSummaryCards totalEstimated={0} totalSpent={5000} />,
    );

    expect(screen.getByText("0%")).toBeInTheDocument();
  });

  it("shows warning color when usage above 90%", () => {
    render(
      <WeddingFinancesSummaryCards totalEstimated={1000} totalSpent={950} />,
    );

    const usage = screen.getByText("95%");
    expect(usage.className).toContain("text-red-500");
  });

  it("shows percentage above 100% in label while Progress value is clamped at 100", () => {
    render(
      <WeddingFinancesSummaryCards totalEstimated={1000} totalSpent={2000} />,
    );

    expect(screen.getByText("200%")).toBeInTheDocument();
  });

  it("does not render average comparison when comparison_percentage is null or undefined", () => {
    const budget = createMockBudget({
      comparison_percentage: null,
      tenant_average_budget: null,
    });

    render(
      <WeddingFinancesSummaryCards
        budget={budget}
        totalEstimated={50000}
        totalSpent={25000}
      />,
    );

    expect(screen.queryByText(/que a média/)).not.toBeInTheDocument();
    expect(screen.queryByText(/média dos casamentos/)).not.toBeInTheDocument();
  });

  it("renders percentage greater than average when budget is above average", () => {
    const budget = createMockBudget({
      comparison_percentage: 50,
      tenant_average_budget: "50000.00",
    });

    render(
      <WeddingFinancesSummaryCards
        budget={budget}
        totalEstimated={75000}
        totalSpent={25000}
      />,
    );

    expect(screen.getByText("50% maior que a média")).toBeInTheDocument();
  });

  it("renders percentage less than average when budget is below average", () => {
    const budget = createMockBudget({
      comparison_percentage: -30,
      tenant_average_budget: "100000.00",
    });

    render(
      <WeddingFinancesSummaryCards
        budget={budget}
        totalEstimated={70000}
        totalSpent={25000}
      />,
    );

    expect(screen.getByText("30% menor que a média")).toBeInTheDocument();
  });

  it("renders 'Na média dos casamentos' when budget is equal to average", () => {
    const budget = createMockBudget({
      comparison_percentage: 0,
      tenant_average_budget: "50000.00",
    });

    render(
      <WeddingFinancesSummaryCards
        budget={budget}
        totalEstimated={50000}
        totalSpent={25000}
      />,
    );

    expect(screen.getByText("Na média dos casamentos")).toBeInTheDocument();
  });

  it("shows 'Dentro do planejado' when budget usage is under 90%", () => {
    render(
      <WeddingFinancesSummaryCards totalEstimated={10000} totalSpent={5000} />,
    );

    expect(screen.getByText("Dentro do planejado")).toBeInTheDocument();
  });

  it("shows attention warning status when budget usage is between 90% and 100%", () => {
    render(
      <WeddingFinancesSummaryCards totalEstimated={10000} totalSpent={9500} />,
    );

    expect(screen.getByText("Atenção: 95% utilizado")).toBeInTheDocument();
  });

  it("shows 'Acima do orçamento' status when budget usage is over 100%", () => {
    render(
      <WeddingFinancesSummaryCards totalEstimated={10000} totalSpent={11000} />,
    );

    expect(screen.getByText("Acima do orçamento")).toBeInTheDocument();
  });

  it("shows 'Dentro do planejado' when budget is 0 and spent is 0", () => {
    render(
      <WeddingFinancesSummaryCards totalEstimated={0} totalSpent={0} />,
    );

    expect(screen.getByText("Dentro do planejado")).toBeInTheDocument();
  });

  it("shows 'Acima do orçamento' when budget is 0 and spent is greater than 0", () => {
    render(
      <WeddingFinancesSummaryCards totalEstimated={0} totalSpent={500} />,
    );

    expect(screen.getByText("Acima do orçamento")).toBeInTheDocument();
  });
});
