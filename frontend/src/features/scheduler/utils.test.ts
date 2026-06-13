import { describe, expect, it } from "vitest";
import { toISODateTime, toDateTimeLocalValue } from "@/features/scheduler/utils";

describe("toISODateTime", () => {
  it("returns empty string for empty input", () => {
    expect(toISODateTime("")).toBe("");
  });

  it("converts a valid datetime-local string to ISO 8601 format", () => {
    const result = toISODateTime("2026-08-15T09:00");
    expect(result).toMatch(/^2026-08-15T09:00:00/);
  });

  it("includes timezone offset or Z suffix in the output", () => {
    const result = toISODateTime("2026-08-15T09:00");
    const tzSuffix = result.slice(19);
    expect(tzSuffix).toMatch(/^([+-]\d{2}:\d{2}|Z)$/);
  });

  it("handles midnight correctly", () => {
    const result = toISODateTime("2026-12-25T00:00");
    expect(result).toMatch(/^2026-12-25T00:00:00/);
  });
});

describe("toDateTimeLocalValue", () => {
  it("returns empty string for empty input", () => {
    expect(toDateTimeLocalValue("")).toBe("");
  });

  it("converts a valid ISO string with timezone offset to datetime-local format", () => {
    // With explicit timezone offset matching local time, the output
    // matches the input's time components regardless of runtime timezone.
    const offset = new Date().getTimezoneOffset();
    const offsetHours = Math.abs(Math.floor(offset / 60));
    const offsetSign = offset <= 0 ? "+" : "-";
    const tz = `${offsetSign}${String(offsetHours).padStart(2, "0")}:00`;
    const isoString = `2026-08-15T09:00:00${tz}`;

    const result = toDateTimeLocalValue(isoString);
    expect(result).toBe("2026-08-15T09:00");
  });

  it("converts ISO string with Z suffix to local datetime-local format", () => {
    const result = toDateTimeLocalValue("2026-08-15T12:00:00Z");
    // The result will be in local time, but we only verify the format
    expect(result).toMatch(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}$/);
    // The date part should still be 2026-08-15 (since 12:00 UTC doesn't
    // cross midnight in most timezones)
    expect(result).toMatch(/^2026-08-15T/);
  });

  it("pads single-digit months and days correctly", () => {
    // Use a timezone-aware offset to avoid timezone issues
    const offset = new Date().getTimezoneOffset();
    const offsetHours = Math.abs(Math.floor(offset / 60));
    const offsetSign = offset <= 0 ? "+" : "-";
    const tz = `${offsetSign}${String(offsetHours).padStart(2, "0")}:00`;
    const isoString = `2026-03-05T07:08:00${tz}`;

    const result = toDateTimeLocalValue(isoString);
    expect(result).toBe("2026-03-05T07:08");
  });

  it("pads single-digit hours and minutes correctly", () => {
    const offset = new Date().getTimezoneOffset();
    const offsetHours = Math.abs(Math.floor(offset / 60));
    const offsetSign = offset <= 0 ? "+" : "-";
    const tz = `${offsetSign}${String(offsetHours).padStart(2, "0")}:00`;
    const isoString = `2026-03-05T05:03:00${tz}`;

    const result = toDateTimeLocalValue(isoString);
    expect(result).toBe("2026-03-05T05:03");
  });
});
