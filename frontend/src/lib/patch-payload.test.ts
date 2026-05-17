import { describe, expect, it } from "vitest";
import { buildPatchPayload } from "@/lib/patch-payload";

describe("buildPatchPayload", () => {
  it("returns empty object when nothing changed", () => {
    const original = { name: "João", email: "joao@email.com", age: 30 };
    const modified = { name: "João", email: "joao@email.com", age: 30 };
    const keys = ["name", "email", "age"] as const;

    const result = buildPatchPayload(original, modified, keys);

    expect(result).toEqual({});
  });

  it("returns only the changed fields", () => {
    const original = { name: "João", email: "joao@email.com", age: 30 };
    const modified = { name: "José", email: "joao@email.com", age: 30 };
    const keys = ["name", "email", "age"] as const;

    const result = buildPatchPayload(original, modified, keys);

    expect(result).toEqual({ name: "José" });
  });

  it("handles multiple changed fields simultaneously", () => {
    const original = { name: "João", email: "joao@email.com", age: 30 };
    const modified = { name: "José", email: "jose@email.com", age: 31 };
    const keys = ["name", "email", "age"] as const;

    const result = buildPatchPayload(original, modified, keys);

    expect(result).toEqual({
      name: "José",
      email: "jose@email.com",
      age: 31,
    });
  });

  it("includes all keys when everything changed", () => {
    const original = { name: "João", email: "joao@email.com", age: 30 };
    const modified = { name: "Maria", email: "maria@email.com", age: 25 };
    const keys = ["name", "email", "age"] as const;

    const result = buildPatchPayload(original, modified, keys);

    expect(result).toEqual({
      name: "Maria",
      email: "maria@email.com",
      age: 25,
    });
  });

  it("ignores keys not present in the keys array even if values differ", () => {
    const original = { name: "João", email: "joao@email.com", age: 30 };
    const modified = { name: "José", email: "jose@email.com", age: 31 };
    const keys = ["name"] as const;

    const result = buildPatchPayload(original, modified, keys);

    expect(result).toEqual({ name: "José" });
    expect(result).not.toHaveProperty("email");
    expect(result).not.toHaveProperty("age");
  });

  it("treats different types as changed", () => {
    const original: Record<string, unknown> = { value: 42 };
    const modified = { value: "42" as unknown };
    const keys = ["value"] as const;

    const result = buildPatchPayload(original, modified, keys);

    expect(result).toEqual({ value: "42" });
  });
});
