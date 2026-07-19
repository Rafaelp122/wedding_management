import { describe, expect, it } from "vitest";
import { getMonthlyWeddingsData, getCashFlowData, getTasksProgressData } from "./chart-helpers";
import type { WeddingByMonthOut } from "@/api/generated/v1/models/weddingByMonthOut";
import type { InstallmentOut } from "@/api/generated/v1/models/installmentOut";
import type { WeddingOut } from "@/api/generated/v1/models/weddingOut";
import type { TaskOut } from "@/api/generated/v1/models/taskOut";

describe("chart-helpers", () => {
  describe("getMonthlyWeddingsData", () => {
    it("correctly aggregates wedding counts per month", () => {
      const input: WeddingByMonthOut[] = [
        { month: 1, count: 2 },
        { month: 6, count: 5 },
        { month: 12, count: 1 },
      ];
      const result = getMonthlyWeddingsData(input);
      expect(result.hasData).toBe(true);
      expect(result.monthlyData[0]).toEqual({ name: "Jan", casamentos: 2 });
      expect(result.monthlyData[5]).toEqual({ name: "Jun", casamentos: 5 });
      expect(result.monthlyData[11]).toEqual({ name: "Dez", casamentos: 1 });
      expect(result.monthlyData[1]).toEqual({ name: "Fev", casamentos: 0 });
    });

    it("returns false for hasData if there are no weddings", () => {
      const result = getMonthlyWeddingsData([]);
      expect(result.hasData).toBe(false);
      expect(result.monthlyData.every((d) => d.casamentos === 0)).toBe(true);
    });
  });

  describe("getCashFlowData", () => {
    it("correctly calculates paid and pending amounts for selected year", () => {
      const input = [
        { uuid: "1", amount: "1000.00", due_date: "2026-01-15", status: "PAID" },
        { uuid: "2", amount: "500.00", due_date: "2026-01-20", status: "PENDING" },
        { uuid: "3", amount: "2000.00", due_date: "2026-06-10", status: "PAID" },
        { uuid: "4", amount: "1500.00", due_date: "2025-01-15", status: "PAID" }, // different year
      ] as unknown as InstallmentOut[];
      const result = getCashFlowData(input, 2026);
      expect(result.hasCashFlowData).toBe(true);
      expect(result.cashFlowData[0]).toEqual({ name: "Jan", pago: 1000, pendente: 500 });
      expect(result.cashFlowData[5]).toEqual({ name: "Jun", pago: 2000, pendente: 0 });
      expect(result.cashFlowData[11]).toEqual({ name: "Dez", pago: 0, pendente: 0 });
    });

    it("returns false for hasCashFlowData when no installments match the year", () => {
      const input = [
        { uuid: "1", amount: "1000.00", due_date: "2025-01-15", status: "PAID" },
      ] as unknown as InstallmentOut[];
      const result = getCashFlowData(input, 2026);
      expect(result.hasCashFlowData).toBe(false);
      expect(result.cashFlowData.every((d) => d.pago === 0 && d.pendente === 0)).toBe(true);
    });
  });

  describe("getTasksProgressData", () => {
    it("filters weddings by year, computes completed task percentage, sorts and limits to top 10", () => {
      const weddings = [
        { uuid: "w1", bride_name: "Alice Smith", groom_name: "Bob Jones", date: "2026-05-20", status: "ACTIVE" },
        { uuid: "w2", bride_name: "Carol White", groom_name: "Dave Brown", date: "2026-08-15", status: "ACTIVE" },
        { uuid: "w3", bride_name: "Eve Green", groom_name: "Frank Black", date: "2025-08-15", status: "ACTIVE" }, // different year
      ] as unknown as WeddingOut[];
      const tasks = [
        { uuid: "t1", wedding: "w1", title: "Task 1", is_completed: true },
        { uuid: "t2", wedding: "w1", title: "Task 2", is_completed: false },
        { uuid: "t3", wedding: "w2", title: "Task 3", is_completed: true },
        { uuid: "t4", wedding: "w3", title: "Task 4", is_completed: true },
      ] as unknown as TaskOut[];

      const result = getTasksProgressData(weddings, tasks, 2026);
      expect(result.hasTasksData).toBe(true);
      expect(result.tasksData.length).toBe(2);
      // w2 has 1 task completed out of 1 (100%)
      // w1 has 1 task completed out of 2 (50%)
      // w2 comes first because sorted desc
      expect(result.tasksData[0]).toEqual({ name: "Carol & Dave", concluido: 100 });
      expect(result.tasksData[1]).toEqual({ name: "Alice & Bob", concluido: 50 });
    });

    it("returns empty array and false if no weddings in the year", () => {
      const weddings = [
        { uuid: "w3", bride_name: "Eve Green", groom_name: "Frank Black", date: "2025-08-15", status: "ACTIVE" },
      ] as unknown as WeddingOut[];
      const result = getTasksProgressData(weddings, [], 2026);
      expect(result.hasTasksData).toBe(false);
      expect(result.tasksData).toEqual([]);
    });
  });
});
