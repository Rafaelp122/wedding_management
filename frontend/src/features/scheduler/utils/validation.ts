import { z } from "zod";
import { parseISO, startOfDay } from "date-fns";
import { SchedulerEventsCreateBody } from "@/api/generated/v1/zod/scheduler/scheduler";

/** Valida os dados de criação de evento, incluindo a BR-VAL02. */
export const createEventSchema = SchedulerEventsCreateBody.superRefine((data, ctx) => {
  if (
    data.start_time &&
    startOfDay(parseISO(data.start_time)) < startOfDay(new Date())
  ) {
    ctx.addIssue({
      code: z.ZodIssueCode.custom,
      message: "Data/hora de início não pode estar no passado.",
      path: ["start_time"],
    });
  }

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

/** Dados validados do formulário de criação de evento. */
export type CreateEventFormData = z.infer<typeof createEventSchema>;
