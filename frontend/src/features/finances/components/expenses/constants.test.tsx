import { describe, expect, it } from "vitest";
import { statusVariant, statusLabel, installmentStatusBadge } from "./constants";

describe("Expenses Constants", () => {
  it("should have correct statusVariant mappings", () => {
    expect(statusVariant.PAID).toBe("default");
    expect(statusVariant.SETTLED).toBe("default");
    expect(statusVariant.PARTIALLY_PAID).toBe("outline");
    expect(statusVariant.PENDING).toBe("outline");
    expect(statusVariant.OVERDUE).toBe("destructive");
  });

  it("should have correct statusLabel mappings", () => {
    expect(statusLabel.PAID).toBe("Pago");
    expect(statusLabel.SETTLED).toBe("Quitada");
    expect(statusLabel.PARTIALLY_PAID).toBe("Parcial");
    expect(statusLabel.PENDING).toBe("Pendente");
    expect(statusLabel.OVERDUE).toBe("Atrasado");
  });

  it("should have correct installmentStatusBadge structure", () => {
    expect(installmentStatusBadge.PAID).toBeDefined();
    expect(installmentStatusBadge.PAID.variant).toBe("default");
    expect(installmentStatusBadge.PAID.label).toBe("Pago");
    expect(installmentStatusBadge.PAID.icon).toBeDefined();

    expect(installmentStatusBadge.PENDING).toBeDefined();
    expect(installmentStatusBadge.PENDING.variant).toBe("outline");
    expect(installmentStatusBadge.PENDING.label).toBe("Pendente");
    expect(installmentStatusBadge.PENDING.icon).toBeDefined();

    expect(installmentStatusBadge.OVERDUE).toBeDefined();
    expect(installmentStatusBadge.OVERDUE.variant).toBe("destructive");
    expect(installmentStatusBadge.OVERDUE.label).toBe("Atrasado");
    expect(installmentStatusBadge.OVERDUE.icon).toBeDefined();
  });
});
