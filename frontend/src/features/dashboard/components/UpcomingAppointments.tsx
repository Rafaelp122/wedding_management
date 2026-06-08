import { Link } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useSchedulerEventsList } from "@/api/generated/v1/endpoints/scheduler/scheduler";
import { Skeleton } from "@/components/ui/skeleton";
import { Calendar } from "lucide-react";

interface UpcomingAppointmentsProps {
  weddingUuid?: string;
}

const formatEventTime = (dateStr: string) => {
  const date = new Date(dateStr);
  const today = new Date();
  const tomorrow = new Date();
  tomorrow.setDate(today.getDate() + 1);

  const isToday = date.toDateString() === today.toDateString();
  const isTomorrow = date.toDateString() === tomorrow.toDateString();

  const time = date.toLocaleTimeString("pt-BR", {
    hour: "2-digit",
    minute: "2-digit",
    timeZone: "UTC",
  });

  if (isToday) return `HOJE, ${time}`;
  if (isTomorrow) return `AMANHÃ, ${time}`;

  return date.toLocaleDateString("pt-BR", {
    day: "2-digit",
    month: "short",
    timeZone: "UTC",
  }).toUpperCase() + `, ${time}`;
};

export function UpcomingAppointments({ weddingUuid }: UpcomingAppointmentsProps) {
  const now = new Date().toISOString();

  const { data: eventsRes, isLoading } = useSchedulerEventsList({
    limit: 100,
    ...(weddingUuid ? { wedding_id: weddingUuid } : {}),
  });

  const events = (eventsRes?.data?.items ?? [])
    .filter((e) => e.start_time >= now)
    .sort((a, b) => a.start_time.localeCompare(b.start_time))
    .slice(0, 5);

  const schedulerLink = weddingUuid
    ? `/weddings/${weddingUuid}?tab=planning&subtab=timeline`
    : "/scheduler";

  return (
    <Card className="bg-card shadow-soft border-zinc-200 dark:border-zinc-800 flex flex-col h-full overflow-hidden">
      <CardHeader className="flex flex-row items-center justify-between pb-4 border-b border-zinc-100 dark:border-zinc-800/50 shrink-0">
        <CardTitle className="text-base font-semibold text-zinc-900 dark:text-white">
          Agenda
        </CardTitle>
        <Button
          asChild
          variant="link"
          className="text-sm text-primary hover:text-primary/80 p-0 h-auto font-medium transition-colors"
        >
          <Link to={schedulerLink}>Ver calendário</Link>
        </Button>
      </CardHeader>

      <CardContent className="p-6 flex-1 overflow-y-auto min-h-[300px]">
        {isLoading ? (
          <div className="space-y-5">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="flex gap-4">
                <Skeleton className="w-3 h-3 rounded-full mt-1 shrink-0" />
                <div className="space-y-1.5 flex-1">
                  <Skeleton className="h-3 w-20" />
                  <Skeleton className="h-4 w-48" />
                  <Skeleton className="h-3 w-32" />
                </div>
              </div>
            ))}
          </div>
        ) : events.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center py-8">
            <Calendar className="w-8 h-8 text-zinc-300 dark:text-zinc-600 mb-3" />
            <p className="text-sm text-zinc-500 dark:text-zinc-400">
              {weddingUuid
                ? "Nenhum evento agendado para este casamento."
                : "Nenhum evento próximo."}
            </p>
          </div>
        ) : (
          <div className="relative border-l-2 border-zinc-100 dark:border-zinc-800/60 ml-2.5 space-y-6">
            {events.map((event, idx) => {
              const isFirst = idx === 0;
              return (
                <div key={event.uuid} className="relative pl-6">
                  <span
                    className={`absolute -left-[7px] top-1 w-3 h-3 rounded-full ring-4 ring-card ${
                      isFirst
                        ? "bg-primary"
                        : "bg-zinc-300 dark:bg-zinc-700"
                    }`}
                  />
                  <div className="flex flex-col">
                    <span
                      className={`text-xs font-bold mb-1 ${
                        isFirst
                          ? "text-primary"
                          : "text-zinc-500 dark:text-zinc-400"
                      }`}
                    >
                      {formatEventTime(event.start_time)}
                    </span>
                    <span className="font-medium text-zinc-900 dark:text-white text-sm">
                      {event.title}
                    </span>
                    {event.description && (
                      <span className="text-xs text-zinc-500 dark:text-zinc-400 mt-1 line-clamp-1">
                        {event.description}
                      </span>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
