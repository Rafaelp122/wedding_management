import { describe, expect, it } from "vitest";
import { mapSchedulerSummary } from "./scheduler-helpers";
import type { SchedulerSummaryOut } from "@/api/generated/v1/models/schedulerSummaryOut";

describe("mapSchedulerSummary", () => {
  it("should return zeros when summary is null or undefined", () => {
    expect(mapSchedulerSummary(undefined)).toEqual({
      total: 0,
      upcoming: 0,
      withReminder: 0,
    });
    expect(mapSchedulerSummary(null)).toEqual({
      total: 0,
      upcoming: 0,
      withReminder: 0,
    });
  });

  it("should map SchedulerSummaryOut fields correctly", () => {
    const apiSummary: SchedulerSummaryOut = {
      total: 15,
      upcoming_7_days: 4,
      with_reminder: 6,
    };

    const result = mapSchedulerSummary(apiSummary);

    expect(result).toEqual({
      total: 15,
      upcoming: 4,
      withReminder: 6,
    });
  });
});
