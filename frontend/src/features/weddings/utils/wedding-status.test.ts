import { describe, expect, it } from "vitest";
import {
  getWeddingStatusInfo,
  getWeddingStatusLabel,
  getWeddingStatusBadgeStyle,
  getWeddingAvatarStyle,
  getWeddingInitials,
} from "@/features/weddings/utils/wedding-status";
import { WeddingStatusEnum } from "@/api/generated/v1/models/weddingStatusEnum";

describe("getWeddingStatusInfo", () => {
  it('returns "Em Andamento" for IN_PROGRESS status', () => {
    const info = getWeddingStatusInfo(WeddingStatusEnum.IN_PROGRESS);
    expect(info.label).toBe("Em Andamento");
    expect(info.variant).toBe("default");
  });

  it('returns "Concluído" for COMPLETED status', () => {
    const info = getWeddingStatusInfo(WeddingStatusEnum.COMPLETED);
    expect(info.label).toBe("Concluído");
    expect(info.variant).toBe("secondary");
  });

  it('returns "Cancelado" for CANCELED status', () => {
    const info = getWeddingStatusInfo(WeddingStatusEnum.CANCELED);
    expect(info.label).toBe("Cancelado");
    expect(info.variant).toBe("destructive");
  });

  it("falls back to IN_PROGRESS for undefined status", () => {
    const info = getWeddingStatusInfo(undefined);
    expect(info.label).toBe("Em Andamento");
  });

  it("falls back to IN_PROGRESS for unknown status", () => {
    const info = getWeddingStatusInfo("UNKNOWN" as unknown as WeddingStatusEnum);
    expect(info.label).toBe("Em Andamento");
  });
});

describe("getWeddingStatusLabel", () => {
  it("returns the label for a valid status", () => {
    expect(getWeddingStatusLabel(WeddingStatusEnum.COMPLETED)).toBe("Concluído");
  });

  it("returns IN_PROGRESS label for undefined", () => {
    expect(getWeddingStatusLabel(undefined)).toBe("Em Andamento");
  });
});

describe("getWeddingStatusBadgeStyle", () => {
  it("returns aura classes for IN_PROGRESS", () => {
    const style = getWeddingStatusBadgeStyle(WeddingStatusEnum.IN_PROGRESS);
    expect(style.className).toContain("bg-aura-50");
    expect(style.dotClassName).toBe("bg-aura-500");
  });

  it("returns emerald classes and check icon for COMPLETED", () => {
    const style = getWeddingStatusBadgeStyle(WeddingStatusEnum.COMPLETED);
    expect(style.className).toContain("bg-emerald-50");
    expect(style.icon).toBe("check");
  });

  it("returns red classes for CANCELED", () => {
    const style = getWeddingStatusBadgeStyle(WeddingStatusEnum.CANCELED);
    expect(style.className).toContain("bg-red-50");
    expect(style.dotClassName).toBe("bg-red-500");
  });

  it("falls back to IN_PROGRESS for unknown status", () => {
    const style = getWeddingStatusBadgeStyle("UNKNOWN" as unknown as WeddingStatusEnum);
    expect(style.className).toContain("bg-aura-50");
  });
});

describe("getWeddingAvatarStyle", () => {
  it("returns aura colors for IN_PROGRESS", () => {
    const style = getWeddingAvatarStyle(WeddingStatusEnum.IN_PROGRESS);
    expect(style.bg).toContain("bg-aura-100");
    expect(style.text).toContain("text-aura-700");
  });

  it("returns emerald colors for COMPLETED", () => {
    const style = getWeddingAvatarStyle(WeddingStatusEnum.COMPLETED);
    expect(style.bg).toContain("bg-emerald-100");
    expect(style.text).toContain("text-emerald-700");
  });

  it("returns red colors for CANCELED", () => {
    const style = getWeddingAvatarStyle(WeddingStatusEnum.CANCELED);
    expect(style.bg).toContain("bg-red-100");
    expect(style.text).toContain("text-red-700");
  });

  it("falls back to IN_PROGRESS for unknown status", () => {
    const style = getWeddingAvatarStyle("UNKNOWN" as unknown as WeddingStatusEnum);
    expect(style.bg).toContain("bg-aura-100");
  });
});

describe("getWeddingInitials", () => {
  it("returns first letters joined by &", () => {
    expect(getWeddingInitials("João", "Maria")).toBe("J&M");
  });

  it("handles names with leading spaces", () => {
    expect(getWeddingInitials("  Pedro", "  Ana")).toBe("P&A");
  });
});
