import type { EventOut } from "@/api/generated/v1/models/eventOut";

export interface SchedulerSummary {
  total: number;
  upcoming: number;
  withReminder: number;
}

/**
 * Ordena os eventos por data/hora de início em ordem crescente.
 */
export function sortEvents(events: EventOut[]): EventOut[] {
  return [...events].sort(
    (left, right) =>
      new Date(left.start_time).getTime() - new Date(right.start_time).getTime()
  );
}

/**
 * Pagina uma lista de eventos com base no deslocamento (offset) e limite (limit).
 */
export function paginateEvents(
  events: EventOut[],
  offset: number,
  limit: number
): EventOut[] {
  return events.slice(offset, offset + limit);
}

/**
 * Calcula o resumo dos eventos do cronograma, utilizando uma data de referência opcional.
 */
export function calculateSchedulerSummary(
  events: EventOut[],
  referenceDate?: Date
): SchedulerSummary {
  const refDate = referenceDate ?? new Date();
  const next7Days = new Date(refDate);
  next7Days.setDate(refDate.getDate() + 7);

  const upcoming = events.filter((event) => {
    const startsAt = new Date(event.start_time);
    return startsAt >= refDate && startsAt <= next7Days;
  }).length;

  const withReminder = events.filter((event) => event.reminder_enabled).length;

  return {
    total: events.length,
    upcoming,
    withReminder,
  };
}
