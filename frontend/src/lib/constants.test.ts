import { describe, expect, it } from "vitest";
import { SELECT_NONE_VALUE } from "./constants";

describe("Global Constants", () => {
  it("should export SELECT_NONE_VALUE as '__none__'", () => {
    expect(SELECT_NONE_VALUE).toBe("__none__");
  });
});
