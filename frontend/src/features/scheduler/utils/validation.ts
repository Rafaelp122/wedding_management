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

/** Valida os dados de criação de item de checklist / tarefa. */
export const createTaskSchema = z.object({
  title: z
    .string()
    .min(1, "O título da tarefa é obrigatório.")
    .max(255, "Máximo de 255 caracteres."),
  description: z.string().optional().default(""),
  priority: z.string().default("MEDIUM"),
  due_date: z
    .string()
    .optional()
    .nullable()
    .transform((val) => (val && val.trim() !== "" ? val : null)),
});

export type CreateTaskFormData = z.input<typeof createTaskSchema>;
