import { describe, expect, it } from "vitest";
import { AxiosError } from "axios";
import { normalizeError } from "@/api/utils/normalize-error";

describe("normalizeError", () => {
  it("returns AxiosError as-is", () => {
    const err = new AxiosError("Network error");

    const result = normalizeError(err);

    expect(result).toBe(err);
  });

  it("returns Error as-is", () => {
    const err = new Error("Something broke");

    const result = normalizeError(err);

    expect(result).toBe(err);
  });

  it("wraps a string in Error", () => {
    const result = normalizeError("plain string");

    expect(result).toBeInstanceOf(Error);
    expect(result.message).toBe("plain string");
  });

  it("wraps a number in Error", () => {
    const result = normalizeError(42);

    expect(result).toBeInstanceOf(Error);
    expect(result.message).toBe("42");
  });

  it("wraps null in Error", () => {
    const result = normalizeError(null);

    expect(result).toBeInstanceOf(Error);
    expect(result.message).toBe("null");
  });

  it("wraps undefined in Error", () => {
    const result = normalizeError(undefined);

    expect(result).toBeInstanceOf(Error);
    expect(result.message).toBe("undefined");
  });
});
