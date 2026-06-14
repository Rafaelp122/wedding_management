/* eslint-disable @typescript-eslint/no-explicit-any */
import { describe, expect, it, vi, beforeEach } from "vitest";
import { render, screen } from "@/test-utils";
import { WeddingFinancesSummaryCards } from "@/features/finances/components/FinancesSummaryCards";
import { useFinancesBudgetsList } from "@/api/generated/v1/endpoints/finances/finances";

vi.mock("@/api/generated/v1/endpoints/finances/finances", async (importOriginal) => {
  const mod = await importOriginal<typeof import("@/api/generated/v1/endpoints/finances/finances")>();
  return {
    ...mod,
    useFinancesBudgetsList: vi.fn(),
  };
});

describe("WeddingFinancesSummaryCards", () => {
  beforeEach(() => {
    vi.mocked(useFinancesBudgetsList).mockReturnValue({
      data: {
        data: {
          items: [],
          count: 0,
        },
      },
      isLoading: false,
    } as any);
  });

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

  it("does not render average comparison when there is only one wedding budget", () => {
    vi.mocked(useFinancesBudgetsList).mockReturnValue({
      data: {
        data: {
          items: [{ total_estimated: "50000" }],
          count: 1,
        },
      },
      isLoading: false,
    } as any);

    render(
      <WeddingFinancesSummaryCards totalEstimated={50000} totalSpent={25000} />,
    );

    expect(screen.queryByText(/que a média/)).not.toBeInTheDocument();
    expect(screen.queryByText(/média dos casamentos/)).not.toBeInTheDocument();
  });

  it("renders percentage greater than average when budget is above average", () => {
    vi.mocked(useFinancesBudgetsList).mockReturnValue({
      data: {
        data: {
          items: [
            { total_estimated: "40000" },
            { total_estimated: "60000" }, // Average is 50000
          ],
          count: 2,
        },
      },
      isLoading: false,
    } as any);

    render(
      <WeddingFinancesSummaryCards totalEstimated={75000} totalSpent={25000} />, // 75000 is 50% greater than 50000
    );

    expect(screen.getByText("50% maior que a média")).toBeInTheDocument();
  });

  it("renders percentage less than average when budget is below average", () => {
    vi.mocked(useFinancesBudgetsList).mockReturnValue({
      data: {
        data: {
          items: [
            { total_estimated: "80000" },
            { total_estimated: "120000" }, // Average is 100000
          ],
          count: 2,
        },
      },
      isLoading: false,
    } as any);

    render(
      <WeddingFinancesSummaryCards totalEstimated={70000} totalSpent={25000} />, // 70000 is 30% less than 100000
    );

    expect(screen.getByText("30% menor que a média")).toBeInTheDocument();
  });

  it("renders 'Na média dos casamentos' when budget is equal to average", () => {
    vi.mocked(useFinancesBudgetsList).mockReturnValue({
      data: {
        data: {
          items: [
            { total_estimated: "50000" },
            { total_estimated: "50000" }, // Average is 50000
          ],
          count: 2,
        },
      },
      isLoading: false,
    } as any);

    render(
      <WeddingFinancesSummaryCards totalEstimated={50000} totalSpent={25000} />,
    );

    expect(screen.getByText("Na média dos casamentos")).toBeInTheDocument();
  });

  it("shows loading skeleton when budgets are loading", () => {
    vi.mocked(useFinancesBudgetsList).mockReturnValue({
      data: undefined,
      isLoading: true,
    } as any);

    render(
      <WeddingFinancesSummaryCards totalEstimated={50000} totalSpent={25000} />,
    );

    const skeletons = document.querySelectorAll(".animate-pulse");
    expect(skeletons.length).toBeGreaterThanOrEqual(1);
  });

  it("does not render average comparison when budgets fetch fails", () => {
    vi.mocked(useFinancesBudgetsList).mockReturnValue({
      data: undefined,
      isLoading: false,
      error: new Error("API Error"),
    } as any);

    render(
      <WeddingFinancesSummaryCards totalEstimated={50000} totalSpent={25000} />,
    );

    expect(screen.queryByText(/que a média/)).not.toBeInTheDocument();
    expect(screen.queryByText(/média dos casamentos/)).not.toBeInTheDocument();
  });

  it("shows 'Dentro do planejado' when budget usage is under 90%", () => {
    render(
      <WeddingFinancesSummaryCards totalEstimated={10000} totalSpent={5000} />, // 50% usage
    );

    expect(screen.getByText("Dentro do planejado")).toBeInTheDocument();
  });

  it("shows attention warning status when budget usage is between 90% and 100%", () => {
    render(
      <WeddingFinancesSummaryCards totalEstimated={10000} totalSpent={9500} />, // 95% usage
    );

    expect(screen.getByText("Atenção: 95% utilizado")).toBeInTheDocument();
  });

  it("shows 'Acima do orçamento' status when budget usage is over 100%", () => {
    render(
      <WeddingFinancesSummaryCards totalEstimated={10000} totalSpent={11000} />, // 110% usage
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
