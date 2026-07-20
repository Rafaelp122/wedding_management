import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { createEventSchema } from "./validation";

describe("createEventSchema", () => {
  beforeEach(() => {
    vi.useFakeTimers();
    vi.setSystemTime(new Date("2026-07-19T12:00:00Z"));
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("should validate a valid event payload", () => {
    const validData = {
      wedding: "wedding-uuid-123",
      title: "Reunião de Alinhamento",
      event_type: "reuniao",
      start_time: "2026-07-20T10:00:00Z",
      end_time: "2026-07-20T11:00:00Z",
      location: "Escritório",
      description: "Discussão de contratos",
      recurrence_rule: "none",
      reminder_enabled: true,
      reminder_minutes_before: 60,
    };

    const parsed = createEventSchema.safeParse(validData);
    expect(parsed.success).toBe(true);
  });

  it("should fail validation if end_time is before or equal to start_time", () => {
    const invalidData = {
      wedding: "wedding-uuid-123",
      title: "Reunião de Alinhamento",
      event_type: "reuniao",
      start_time: "2026-07-20T10:00:00Z",
      end_time: "2026-07-20T09:00:00Z",
      location: "Escritório",
      description: "",
      recurrence_rule: "none",
      reminder_enabled: false,
      reminder_minutes_before: 60,
    };

    const parsed = createEventSchema.safeParse(invalidData);
    expect(parsed.success).toBe(false);
    if (!parsed.success) {
      expect(parsed.error.issues[0].message).toBe(
        "Data/hora de término deve ser posterior ao início."
      );
      expect(parsed.error.issues[0].path).toContain("end_time");
    }
  });

  it("should reject a start_time in the past", () => {
    const invalidData = {
      wedding: "wedding-uuid-123",
      title: "Reunião retroativa",
      event_type: "reuniao",
      start_time: "2026-07-18T10:00:00Z",
      end_time: null,
      location: "Escritório",
      description: "",
      recurrence_rule: "none",
      reminder_enabled: false,
      reminder_minutes_before: 60,
    };

    const parsed = createEventSchema.safeParse(invalidData);

    expect(parsed.success).toBe(false);
    if (!parsed.success) {
      expect(parsed.error.issues[0]).toMatchObject({
        message: "Data/hora de início não pode estar no passado.",
        path: ["start_time"],
      });
    }
  });

  it("should allow an earlier time on the current date", () => {
    const parsed = createEventSchema.safeParse({
      wedding: "wedding-uuid-123",
      title: "Pagamento de hoje",
      event_type: "pagamento",
      start_time: "2026-07-19T09:00:00Z",
      end_time: null,
      location: "",
      description: "",
      recurrence_rule: "none",
      reminder_enabled: false,
      reminder_minutes_before: 60,
    });

    expect(parsed.success).toBe(true);
  });

  it("should allow end_time to be null", () => {
    const validDataWithNullEnd = {
      wedding: "wedding-uuid-123",
      title: "Reunião de Alinhamento",
      event_type: "reuniao",
      start_time: "2026-07-20T10:00:00Z",
      end_time: null,
      location: "Escritório",
      description: "",
      recurrence_rule: "none",
      reminder_enabled: false,
      reminder_minutes_before: 60,
    };

    const parsed = createEventSchema.safeParse(validDataWithNullEnd);
    expect(parsed.success).toBe(true);
  });
});
