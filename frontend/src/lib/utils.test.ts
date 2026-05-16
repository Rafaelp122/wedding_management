import { describe, expect, it } from "vitest";
import { cn } from "@/lib/utils";

describe("cn", () => {
  it("merges class names", () => {
    expect(cn("foo", "bar")).toBe("foo bar");
  });

  it("handles conditional classes", () => {
    expect(cn("base", undefined, null, "visible")).toBe(
      "base visible",
    );
  });

  it("resolves tailwind conflicts", () => {
    expect(cn("px-4 py-2", "px-6")).toBe("py-2 px-6");
  });

  it("returns empty string for no arguments", () => {
    expect(cn()).toBe("");
  });

  it("handles arrays", () => {
    expect(cn(["flex", "gap-2"], "p-4")).toBe("flex gap-2 p-4");
  });
});
