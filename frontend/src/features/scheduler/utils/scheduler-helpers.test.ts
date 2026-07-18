import { describe, expect, it } from "vitest";
import type { EventOut } from "@/api/generated/v1/models/eventOut";
import {
  sortEvents,
  paginateEvents,
  calculateSchedulerSummary,
} from "./scheduler-helpers";

const mockEvents: EventOut[] = [
  {
    uuid: "1",
    wedding: "wedding-1",
    company_id: "company-1",
    title: "Event 1",
    event_type: "reuniao",
    start_time: "2026-07-20T10:00:00Z",
    end_time: "2026-07-20T11:00:00Z",
    recurrence_rule: "none",
    reminder_enabled: true,
    reminder_minutes_before: 60,
  },
  {
    uuid: "2",
    wedding: "wedding-1",
    company_id: "company-1",
    title: "Event 2",
    event_type: "visita",
    start_time: "2026-07-18T14:00:00Z",
    end_time: "2026-07-18T15:00:00Z",
    recurrence_rule: "none",
    reminder_enabled: false,
    reminder_minutes_before: 60,
  },
  {
    uuid: "3",
    wedding: "wedding-1",
    company_id: "company-1",
    title: "Event 3",
    event_type: "pagamento",
    start_time: "2026-07-24T09:00:00Z",
    end_time: null,
    recurrence_rule: "none",
    reminder_enabled: true,
    reminder_minutes_before: 60,
  },
];

describe("sortEvents", () => {
  it("should sort events by start_time ascending", () => {
    const sorted = sortEvents(mockEvents);
    expect(sorted[0].uuid).toBe("2"); // 2026-07-18
    expect(sorted[1].uuid).toBe("1"); // 2026-07-20
    expect(sorted[2].uuid).toBe("3"); // 2026-07-25
  });
});

describe("paginateEvents", () => {
  it("should return the correct slice of events", () => {
    const paginated = paginateEvents(mockEvents, 1, 2);
    expect(paginated.length).toBe(2);
    expect(paginated[0].uuid).toBe("2");
    expect(paginated[1].uuid).toBe("3");
  });
});

describe("calculateSchedulerSummary", () => {
  it("should calculate total events, upcoming events in next 7 days, and events with reminder enabled", () => {
    const referenceDate = new Date("2026-07-18T00:00:00Z");
    const summary = calculateSchedulerSummary(mockEvents, referenceDate);

    expect(summary.total).toBe(3);
    // Upcoming within 7 days from 2026-07-18 (ends on 2026-07-25 inclusive)
    // Event 2 (July 18) -> Yes
    // Event 1 (July 20) -> Yes
    // Event 3 (July 25) -> Yes
    expect(summary.upcoming).toBe(3);
    // reminder_enabled: Event 1 (true), Event 3 (true) -> 2
    expect(summary.withReminder).toBe(2);
  });

  it("should filter out events past the next 7 days or in the past", () => {
    const referenceDate = new Date("2026-07-21T00:00:00Z");
    const summary = calculateSchedulerSummary(mockEvents, referenceDate);

    expect(summary.total).toBe(3);
    // Event 1 (July 20) -> Past
    // Event 2 (July 18) -> Past
    // Event 3 (July 25) -> Yes (within next 7 days until 2026-07-28)
    expect(summary.upcoming).toBe(1);
  });
});
