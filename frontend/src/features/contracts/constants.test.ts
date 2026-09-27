import { describe, expect, it } from "vitest";
import {
  STATUS_STYLES,
  STATUS_LABELS,
  CONTRACT_STATUS_OPTIONS,
} from "./constants";

describe("Contracts Constants", () => {
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

  it("should have correct CONTRACT_STATUS_OPTIONS", () => {
    expect(CONTRACT_STATUS_OPTIONS).toEqual([
      { value: "DRAFT", label: "Rascunho" },
      { value: "PENDING", label: "Pendente" },
      { value: "SIGNED", label: "Assinado" },
      { value: "CANCELED", label: "Cancelado" },
    ]);
  });
});
