import type { SchedulerSummaryOut } from "@/api/generated/v1/models/schedulerSummaryOut";

export interface SchedulerSummary {
  total: number;
  upcoming: number;
  withReminder: number;
}

/**
 * Converte o resumo estatístico retornado pela API no formato consumido pelos componentes visuais.
 */
export function mapSchedulerSummary(
  summary?: SchedulerSummaryOut | null,
): SchedulerSummary {
  return {
    total: summary?.total ?? 0,
    upcoming: summary?.upcoming_7_days ?? 0,
    withReminder: summary?.with_reminder ?? 0,
  };
}
