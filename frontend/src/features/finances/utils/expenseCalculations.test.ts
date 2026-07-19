import { describe, it, expect } from "vitest";
import { calculateExpenseProgress } from "./expenseCalculations";

describe("calculateExpenseProgress", () => {
  it("should return 0 if actual_amount is 0 or less", () => {
    expect(calculateExpenseProgress({ total_paid: 100, actual_amount: 0 })).toBe(0);
    expect(calculateExpenseProgress({ total_paid: 100, actual_amount: -10 })).toBe(0);
    expect(calculateExpenseProgress({ total_paid: 100, actual_amount: null })).toBe(0);
  });

  it("should calculate correct percentage progress", () => {
    expect(calculateExpenseProgress({ total_paid: 50, actual_amount: 100 })).toBe(50);
    expect(calculateExpenseProgress({ total_paid: "25.00", actual_amount: "100.00" })).toBe(25);
    expect(calculateExpenseProgress({ total_paid: 33.33, actual_amount: 100 })).toBe(33);
  });

  it("should not exceed 100%", () => {
    expect(calculateExpenseProgress({ total_paid: 120, actual_amount: 100 })).toBe(100);
  });

  it("should handle null or undefined total_paid", () => {
    expect(calculateExpenseProgress({ total_paid: null, actual_amount: 100 })).toBe(0);
    expect(calculateExpenseProgress({ total_paid: undefined, actual_amount: 100 })).toBe(0);
  });
});
