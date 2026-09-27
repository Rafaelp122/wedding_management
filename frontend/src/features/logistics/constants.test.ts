import { describe, expect, it } from "vitest";
import {
  ITEM_STATUS_STYLES,
  ITEM_STATUS_LABELS,
  ACQUISITION_STATUS_OPTIONS,
  INITIAL_SCOPE_OPTIONS,
} from "./constants";

describe("Logistics Constants", () => {
  it("should have correct ITEM_STATUS_STYLES mapping", () => {
    expect(ITEM_STATUS_STYLES.PENDING).toBe("bg-yellow-100 text-yellow-800 border-yellow-200");
    expect(ITEM_STATUS_STYLES.IN_PROGRESS).toBe("bg-blue-100 text-blue-800 border-blue-200");
    expect(ITEM_STATUS_STYLES.DONE).toBe("bg-green-100 text-green-800 border-green-200");
  });

  it("should have correct ITEM_STATUS_LABELS mapping", () => {
    expect(ITEM_STATUS_LABELS.PENDING).toBe("Pendente");
    expect(ITEM_STATUS_LABELS.IN_PROGRESS).toBe("Em Andamento");
    expect(ITEM_STATUS_LABELS.DONE).toBe("Concluído");
  });

  it("should have correct ACQUISITION_STATUS_OPTIONS", () => {
    expect(ACQUISITION_STATUS_OPTIONS).toEqual([
      { value: "PENDING", label: "Pendente" },
      { value: "IN_PROGRESS", label: "Em Andamento" },
      { value: "DONE", label: "Concluído" },
    ]);
  });

  it("should have correct INITIAL_SCOPE_OPTIONS", () => {
    expect(INITIAL_SCOPE_OPTIONS).toEqual([
      { value: "INCLUDED", label: "Incluído" },
      { value: "DESIRED", label: "Desejado" },
    ]);
  });
});
