import { describe, expect, it } from "vitest";
import {
  STATUS_STYLES,
  STATUS_LABELS,
  ITEM_STATUS_STYLES,
  ITEM_STATUS_LABELS,
  ACQUISITION_STATUS_OPTIONS,
  CONTRACT_STATUS_OPTIONS,
} from "./constants";

describe("Logistics Constants", () => {
  it("should have correct STATUS_STYLES mapping", () => {
    expect(STATUS_STYLES.DRAFT).toBe("bg-gray-100 text-gray-700");
    expect(STATUS_STYLES.PENDING).toBe("bg-yellow-100 text-yellow-800");
    expect(STATUS_STYLES.SIGNED).toBe("bg-green-100 text-green-800");
    expect(STATUS_STYLES.CANCELED).toBe("bg-red-100 text-red-800");
  });

  it("should have correct STATUS_LABELS mapping", () => {
    expect(STATUS_LABELS.DRAFT).toBe("Rascunho");
    expect(STATUS_LABELS.PENDING).toBe("Pendente");
    expect(STATUS_LABELS.SIGNED).toBe("Assinado");
    expect(STATUS_LABELS.CANCELED).toBe("Cancelado");
  });

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

  it("should have correct CONTRACT_STATUS_OPTIONS", () => {
    expect(CONTRACT_STATUS_OPTIONS).toEqual([
      { value: "DRAFT", label: "Rascunho" },
      { value: "PENDING", label: "Pendente" },
      { value: "SIGNED", label: "Assinado" },
      { value: "CANCELED", label: "Cancelado" },
    ]);
  });
});
