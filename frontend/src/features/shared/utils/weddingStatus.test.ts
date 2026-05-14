import { describe, expect, it } from "vitest";
import {
  getWeddingStatusInfo,
  getWeddingStatusLabel,
} from "@/features/shared/utils/weddingStatus";

describe("getWeddingStatusInfo", () => {
  it('returns "Em Andamento" for IN_PROGRESS status', () => {
    const info = getWeddingStatusInfo("IN_PROGRESS");
    expect(info.label).toBe("Em Andamento");
    expect(info.variant).toBe("default");
  });

  it('returns "Concluído" for COMPLETED status', () => {
    const info = getWeddingStatusInfo("COMPLETED");
    expect(info.label).toBe("Concluído");
    expect(info.variant).toBe("secondary");
  });

  it('returns "Cancelado" for CANCELED status', () => {
    const info = getWeddingStatusInfo("CANCELED");
    expect(info.label).toBe("Cancelado");
    expect(info.variant).toBe("destructive");
  });

  it("falls back to IN_PROGRESS for undefined status", () => {
    const info = getWeddingStatusInfo(undefined);
    expect(info.label).toBe("Em Andamento");
  });

  it("falls back to IN_PROGRESS for unknown status", () => {
    const info = getWeddingStatusInfo("UNKNOWN");
    expect(info.label).toBe("Em Andamento");
  });
});

describe("getWeddingStatusLabel", () => {
  it("returns the label for a valid status", () => {
    expect(getWeddingStatusLabel("COMPLETED")).toBe("Concluído");
  });

  it("returns IN_PROGRESS label for undefined", () => {
    expect(getWeddingStatusLabel(undefined)).toBe("Em Andamento");
  });
});
