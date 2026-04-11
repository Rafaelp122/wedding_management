import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface SchedulerSummary {
  total: number;
  upcoming: number;
  withReminder: number;
}

interface SchedulerSummaryCardsProps {
  summary: SchedulerSummary;
}

export function SchedulerSummaryCards({ summary }: SchedulerSummaryCardsProps) {
  return (
    <div className="grid gap-4 md:grid-cols-3">
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium">Eventos</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-2xl font-bold">{summary.total}</p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium">Próximos 7 dias</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-2xl font-bold">{summary.upcoming}</p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium">Com lembrete</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-2xl font-bold">{summary.withReminder}</p>
        </CardContent>
      </Card>
    </div>
  );
}
