import { z } from "zod";
import { parseISO } from "date-fns";
import { SchedulerEventsCreateBody } from "@/api/generated/v1/zod/scheduler/scheduler";

export const createEventSchema = SchedulerEventsCreateBody.superRefine((data, ctx) => {
  if (
    data.end_time &&
    data.start_time &&
    parseISO(data.end_time) <= parseISO(data.start_time)
  ) {
    ctx.addIssue({
      code: z.ZodIssueCode.custom,
      message: "Data/hora de término deve ser posterior ao início.",
      path: ["end_time"],
    });
  }
});

export type CreateEventFormData = z.infer<typeof createEventSchema>;
