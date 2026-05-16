import { describe, expect, it } from "vitest";
import { render, screen } from "@/test-utils";
import { WeddingFinancesSummaryCards } from "@/features/finances/components/FinancesSummaryCards";

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

  it("caps usage at 100%", () => {
    render(
      <WeddingFinancesSummaryCards totalEstimated={1000} totalSpent={2000} />,
    );

    expect(screen.getByText("200%")).toBeInTheDocument();
  });
});
