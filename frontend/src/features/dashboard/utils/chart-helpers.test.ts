import { describe, expect, it } from "vitest";
import {
  getMonthlyWeddingsData,
  formatCashFlowData,
  formatTasksProgressData,
} from "./chart-helpers";
import type { WeddingByMonthOut } from "@/api/generated/v1/models/weddingByMonthOut";
import type { CashFlowMonthOut } from "@/api/generated/v1/models/cashFlowMonthOut";
import type { TaskProgressWeddingOut } from "@/api/generated/v1/models/taskProgressWeddingOut";

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

  describe("formatCashFlowData", () => {
    it("formats backend cash flow projection into chart items", () => {
      const input: CashFlowMonthOut[] = [
        { month: 1, paid: "1000.00", pending: "500.00" },
        { month: 6, paid: "2000.00", pending: "0.00" },
      ];
      const result = formatCashFlowData(input);
      expect(result.hasCashFlowData).toBe(true);
      expect(result.cashFlowData[0]).toEqual({ name: "Jan", pago: 1000, pendente: 500 });
      expect(result.cashFlowData[1]).toEqual({ name: "Jun", pago: 2000, pendente: 0 });
    });

    it("returns false for hasCashFlowData when list is empty or zero amounts", () => {
      const resultEmpty = formatCashFlowData([]);
      expect(resultEmpty.hasCashFlowData).toBe(false);
      expect(resultEmpty.cashFlowData).toEqual([]);

      const resultZeros = formatCashFlowData([
        { month: 1, paid: "0.00", pending: "0.00" },
      ]);
      expect(resultZeros.hasCashFlowData).toBe(false);
    });
  });

  describe("formatTasksProgressData", () => {
    it("formats backend task progress records into chart items", () => {
      const input: TaskProgressWeddingOut[] = [
        {
          wedding_uuid: "w-1",
          wedding_name: "Carol & Dave",
          total_tasks: 10,
          completed_tasks: 10,
          progress_pct: 100,
        },
        {
          wedding_uuid: "w-2",
          wedding_name: "Alice & Bob",
          total_tasks: 8,
          completed_tasks: 4,
          progress_pct: 50,
        },
      ];

      const result = formatTasksProgressData(input);
      expect(result.hasTasksData).toBe(true);
      expect(result.tasksData).toHaveLength(2);
      expect(result.tasksData[0]).toEqual({ name: "Carol & Dave", concluido: 100 });
      expect(result.tasksData[1]).toEqual({ name: "Alice & Bob", concluido: 50 });
    });

    it("returns empty array and false when input is empty", () => {
      const result = formatTasksProgressData([]);
      expect(result.hasTasksData).toBe(false);
      expect(result.tasksData).toEqual([]);
    });
  });
});
