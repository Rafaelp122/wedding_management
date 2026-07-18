import { describe, expect, it } from "vitest";
import { createEventSchema } from "./validation";

describe("createEventSchema", () => {
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
      end_time: "2026-07-20T09:00:00Z", // end_time is earlier
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
