import { describe, expect, it } from "vitest";
import { createMockContractAddendum } from "@/test-data";
import {
  amountToCents,
  countAddendumsByStatus,
  filterAddendumsByStatus,
  sumAddendumAmounts,
} from "./addendum-helpers";

describe("addendum-helpers", () => {
  const list = [
    createMockContractAddendum({ uuid: "a1", amount: "1000.00", status: "PENDING" }),
    createMockContractAddendum({ uuid: "a2", amount: "2500.50", status: "SIGNED" }),
    createMockContractAddendum({ uuid: "a3", amount: "100.00", status: "CANCELED" }),
  ];

  it("returns full list on ALL filter", () => {
    expect(filterAddendumsByStatus(list, "ALL")).toBe(list);
  });

  it("filters by each status", () => {
    expect(filterAddendumsByStatus(list, "PENDING").map((a) => a.uuid)).toEqual(["a1"]);
    expect(filterAddendumsByStatus(list, "SIGNED").map((a) => a.uuid)).toEqual(["a2"]);
    expect(filterAddendumsByStatus(list, "CANCELED").map((a) => a.uuid)).toEqual(["a3"]);
  });

  it("sums amounts with cent precision", () => {
    expect(sumAddendumAmounts(list)).toBeCloseTo(3600.5, 2);
    expect(sumAddendumAmounts([])).toBe(0);
    expect(
      sumAddendumAmounts([
        createMockContractAddendum({ amount: "0.10", status: "PENDING" }),
        createMockContractAddendum({ amount: "0.20", status: "PENDING" }),
      ]),
    ).toBe(0.3);
  });

  it("treats invalid amounts as zero", () => {
    expect(amountToCents(null)).toBe(0);
    expect(amountToCents(undefined)).toBe(0);
    expect(amountToCents("abc")).toBe(0);
  });

  it("counts by status", () => {
    expect(countAddendumsByStatus(list)).toEqual({
      ALL: 3,
      PENDING: 1,
      SIGNED: 1,
      CANCELED: 1,
    });
  });
});
