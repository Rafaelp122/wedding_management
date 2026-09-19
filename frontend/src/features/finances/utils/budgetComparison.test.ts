import { describe, expect, it } from "vitest";
import { calculateBudgetComparison } from "./budgetComparison";

describe("calculateBudgetComparison", () => {
  it("returns hasEnoughData=false when less than 2 valid budgets exist", () => {
    const result = calculateBudgetComparison(50000, [
      { total_estimated: "50000.00" },
    ]);
    expect(result.hasEnoughData).toBe(false);
  });

  it("calculates positive diff percentage when current budget is greater than average", () => {
    const result = calculateBudgetComparison(60000, [
      { total_estimated: "40000.00" },
      { total_estimated: "40000.00" },
    ]);
    expect(result.hasEnoughData).toBe(true);
    expect(result.isBudgetGreater).toBe(true);
    expect(result.diffPercentage).toBe(50);
  });

  it("calculates negative diff percentage when current budget is lower than average", () => {
    const result = calculateBudgetComparison(30000, [
      { total_estimated: "60000.00" },
      { total_estimated: "60000.00" },
    ]);
    expect(result.hasEnoughData).toBe(true);
    expect(result.isBudgetGreater).toBe(false);
    expect(result.diffPercentage).toBe(50);
  });

  it("identifies equal budget to average", () => {
    const result = calculateBudgetComparison(50000, [
      { total_estimated: "50000.00" },
      { total_estimated: "50000.00" },
    ]);
    expect(result.hasEnoughData).toBe(true);
    expect(result.isBudgetEqual).toBe(true);
    expect(result.diffPercentage).toBe(0);
  });

  it("returns hasEnoughData=false when budgets list is empty or values are zero/null", () => {
    const emptyResult = calculateBudgetComparison(10000, []);
    expect(emptyResult.hasEnoughData).toBe(false);

    const zeroResult = calculateBudgetComparison(10000, [
      { total_estimated: "0.00" },
      { total_estimated: null },
      { total_estimated: undefined },
    ]);
    expect(zeroResult.hasEnoughData).toBe(false);
  });
});
