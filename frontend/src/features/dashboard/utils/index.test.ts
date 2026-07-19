import { describe, expect, it } from "vitest";
import { formatWeddingName, pluralize } from "./index";

describe("formatWeddingName", () => {
  it("returns bride & groom format", () => {
    expect(formatWeddingName("Maria", "João")).toBe("Maria & João");
  });
});

describe("pluralize", () => {
  it("returns singular for count 1", () => {
    expect(pluralize(1, "pendente")).toBe("pendente");
  });

  it("returns plural for count > 1", () => {
    expect(pluralize(3, "pendente")).toBe("pendentes");
  });

  it("uses custom plural when provided", () => {
    expect(pluralize(2, "parcela", "parcelas")).toBe("parcelas");
  });

  it("returns plural for count 0", () => {
    expect(pluralize(0, "item")).toBe("items");
  });
});
