import { describe, expect, it } from "vitest";
import {
  formatDateBR,
  formatDateTimeBR,
  formatCurrencyBR,
  formatCurrencyBRCompact,
  parseDecimal,
} from "@/lib/formatters";

describe("formatDateBR", () => {
  it("formats a valid date string to pt-BR", () => {
    const result = formatDateBR("2025-06-15");
    expect(result).toContain("15");
    expect(result).toContain("06");
    expect(result).toContain("2025");
  });

  it("returns the input as-is for invalid dates", () => {
    expect(formatDateBR("not-a-date")).toBe("not-a-date");
  });

  it("respects custom options", () => {
    const result = formatDateBR("2025-06-15", {
      year: "numeric",
      month: "long",
      day: "numeric",
    });
    expect(result).toBe("15 de junho de 2025");
  });
});

describe("formatDateTimeBR", () => {
  it("formats a valid datetime string", () => {
    const result = formatDateTimeBR("2025-06-15T14:30:00");
    expect(result).toContain("15");
    expect(result).toContain("06");
    expect(result).toContain("2025");
  });

  it("returns the input as-is for invalid datetimes", () => {
    expect(formatDateTimeBR("invalid")).toBe("invalid");
  });
});

describe("formatCurrencyBR", () => {
  it("formats a number to pt-BR currency", () => {
    const result = formatCurrencyBR(1500.5);
    expect(result).toBe("1.500,50");
  });

  it("handles zero", () => {
    expect(formatCurrencyBR(0)).toBe("0,00");
  });

  it("handles large numbers", () => {
    const result = formatCurrencyBR(1_000_000);
    expect(result).toBe("1.000.000,00");
  });
});

describe("formatCurrencyBRCompact", () => {
  it("prefixes with R$ and includes formatted value", () => {
    const result = formatCurrencyBRCompact(100);
    expect(result.startsWith("R$")).toBe(true);
    expect(result).toContain("100");
  });
});

describe("parseDecimal", () => {
  it("parses a valid number string", () => {
    expect(parseDecimal("123.45")).toBe(123.45);
  });

  it("returns 0 for null", () => {
    expect(parseDecimal(null)).toBe(0);
  });

  it("returns 0 for undefined", () => {
    expect(parseDecimal(undefined)).toBe(0);
  });

  it("returns 0 for empty string", () => {
    expect(parseDecimal("")).toBe(0);
  });

  it("returns 0 for non-numeric strings", () => {
    expect(parseDecimal("abc")).toBe(0);
  });
});
