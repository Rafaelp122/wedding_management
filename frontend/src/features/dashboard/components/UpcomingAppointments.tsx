import { useState } from "react";
import { Link } from "react-router-dom";
import { Clock, Calendar, ArrowUpRight } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useSchedulerEventsList } from "@/api/generated/v1/endpoints/scheduler/scheduler";

const PERIOD_OPTIONS = [7, 14, 30] as const;

export function UpcomingAppointments() {
  const [days, setDays] = useState<number>(7);
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const cutoff = new Date(today);
  cutoff.setDate(cutoff.getDate() + days);

  const { data } = useSchedulerEventsList({ limit: 50 });

  const events = (data?.data?.items ?? [])
    .filter((event) => {
      const eventDate = new Date(event.start_time);
      return eventDate >= today && eventDate <= cutoff;
    })
    .sort((a, b) => new Date(a.start_time).getTime() - new Date(b.start_time).getTime())
    .slice(0, 5);

  const formatEventDate = (dateStr: string) => {
    const date = new Date(dateStr);
    date.setHours(0, 0, 0, 0);
    const now = new Date();
    now.setHours(0, 0, 0, 0);
    const diffDays = Math.ceil((date.getTime() - now.getTime()) / 86400000);
    if (diffDays === 0) return "Hoje";
    if (diffDays === 1) return "Amanhã";
    return new Intl.DateTimeFormat("pt-BR", {
      day: "2-digit",
      month: "short",
      hour: "2-digit",
      minute: "2-digit",
    }).format(date);
  };

  return (
    <Card className="flex flex-col overflow-hidden">
      <CardHeader className="bg-muted/30 border-b pb-4">
        <div className="flex items-center justify-between gap-2">
          <CardTitle className="text-base font-semibold flex items-center gap-2">
            <Clock className="size-4 text-primary" />
            Próximos Compromissos
          </CardTitle>
          <div className="flex items-center gap-0.5 bg-background rounded-md border p-0.5">
            {PERIOD_OPTIONS.map((d) => (
              <button
                key={d}
                onClick={() => setDays(d)}
                className={`px-2 py-0.5 text-xs rounded-sm font-medium transition-colors ${
                  days === d
                    ? "bg-primary text-primary-foreground"
                    : "text-muted-foreground hover:text-foreground"
                }`}
              >
                {d}d
              </button>
            ))}
          </div>
        </div>
      </CardHeader>
      <CardContent className="p-6 flex-1 overflow-y-auto min-h-[300px]">
        {events.length > 0 ? (
          <div className="space-y-6">
            {events.map((event, index) => (
              <div key={event.uuid} className="relative pl-6">
                {index !== events.length - 1 && (
                  <div className="absolute left-[7px] top-6 bottom-[-24px] w-px bg-border" />
                )}
                <div className="absolute left-0 top-1.5 size-4 rounded-full border-2 border-background bg-primary shadow-sm" />
                <div className="space-y-1">
                  <p className="text-sm font-semibold">{event.title}</p>
                  <p className="text-xs text-muted-foreground flex items-center gap-1">
                    <Calendar className="size-3" />{" "}
                    {formatEventDate(event.start_time)}
                  </p>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="h-full flex flex-col items-center justify-center text-muted-foreground py-8">
            <Calendar className="w-8 h-8 text-muted/30 mb-3" />
            <p className="text-sm">Nenhum compromisso nos próximos {days} dias.</p>
          </div>
        )}
      </CardContent>
      <div className="p-4 border-t bg-muted/30">
        <Button asChild variant="ghost" className="w-full text-primary hover:text-primary/80 hover:bg-primary/5 h-9 text-xs gap-1">
          <Link to="/scheduler">
            Ver agenda completa <ArrowUpRight className="size-3" />
          </Link>
        </Button>
      </div>
    </Card>
  );
}
