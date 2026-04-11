import { useMemo } from "react";
import { useSchedulerEventsList } from "@/api/generated/v1/endpoints/scheduler/scheduler";
import { useWeddingsList } from "@/api/generated/v1/endpoints/weddings/weddings";
import { getApiErrorInfo } from "@/api/error-utils";

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { AlertCircle, Calendar, Clock, Bell } from "lucide-react";

const EVENT_LABELS: Record<string, string> = {
  reuniao: "Reunião",
  pagamento: "Pagamento",
  visita: "Visita Técnica",
  degustacao: "Degustação",
  outro: "Outro",
};

const formatDateTime = (value: string): string => {
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return value;

  return parsed.toLocaleString("pt-BR", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
};

export default function AgendaPage() {
  const {
    data: eventsResponse,
    isLoading: isLoadingEvents,
    error: eventsError,
  } = useSchedulerEventsList({ limit: 300 });
  const {
    data: weddingsResponse,
    isLoading: isLoadingWeddings,
    error: weddingsError,
  } = useWeddingsList({ limit: 200 });

  const events = useMemo(() => eventsResponse?.data.items ?? [], [eventsResponse]);
  const weddings = useMemo(
    () => weddingsResponse?.data.items ?? [],
    [weddingsResponse],
  );

  const isLoading = isLoadingEvents || isLoadingWeddings;
  const firstError = eventsError ?? weddingsError;

  const weddingsByUuid = useMemo(
    () =>
      new Map(
        weddings.map((wedding) => [
          wedding.uuid,
          `${wedding.groom_name} & ${wedding.bride_name}`,
        ]),
      ),
    [weddings],
  );

  const sortedEvents = useMemo(
    () =>
      [...events].sort(
        (left, right) =>
          new Date(left.start_time).getTime() - new Date(right.start_time).getTime(),
      ),
    [events],
  );

  const summary = useMemo(() => {
    const now = new Date();
    const next7Days = new Date();
    next7Days.setDate(now.getDate() + 7);

    const upcoming = events.filter((event) => {
      const startsAt = new Date(event.start_time);
      return startsAt >= now && startsAt <= next7Days;
    }).length;

    const withReminder = events.filter((event) => event.reminder_enabled).length;

    return {
      total: events.length,
      upcoming,
      withReminder,
    };
  }, [events]);

  if (isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-10 w-72" />
        <div className="grid gap-4 md:grid-cols-3">
          <Skeleton className="h-28 w-full" />
          <Skeleton className="h-28 w-full" />
          <Skeleton className="h-28 w-full" />
        </div>
        <Skeleton className="h-96 w-full" />
      </div>
    );
  }

  if (firstError) {
    const { message } = getApiErrorInfo(
      firstError,
      "Não foi possível carregar a agenda.",
    );

    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertTitle>Erro ao carregar agenda</AlertTitle>
        <AlertDescription>{message}</AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      <div>
        <h2 className="text-3xl font-bold tracking-tight">Agenda</h2>
        <p className="text-muted-foreground">
          Visão global dos compromissos de todos os casamentos.
        </p>
      </div>

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

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Calendar className="h-5 w-5" />
            Próximos compromissos
          </CardTitle>
          <CardDescription>
            Eventos ordenados por data para facilitar o acompanhamento operacional.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="rounded-md border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Título</TableHead>
                  <TableHead>Casamento</TableHead>
                  <TableHead>Tipo</TableHead>
                  <TableHead>Início</TableHead>
                  <TableHead>Fim</TableHead>
                  <TableHead>Lembrete</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {sortedEvents.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={6} className="text-center text-muted-foreground">
                      Nenhum evento cadastrado até o momento.
                    </TableCell>
                  </TableRow>
                ) : (
                  sortedEvents.map((event) => (
                    <TableRow key={event.uuid}>
                      <TableCell className="font-medium">{event.title}</TableCell>
                      <TableCell>
                        {weddingsByUuid.get(event.wedding) ?? event.wedding}
                      </TableCell>
                      <TableCell>
                        <Badge variant="secondary">
                          {EVENT_LABELS[event.event_type] ?? event.event_type}
                        </Badge>
                      </TableCell>
                      <TableCell>{formatDateTime(event.start_time)}</TableCell>
                      <TableCell>
                        {event.end_time ? formatDateTime(event.end_time) : "—"}
                      </TableCell>
                      <TableCell>
                        {event.reminder_enabled ? (
                          <span className="inline-flex items-center gap-1 text-xs text-muted-foreground">
                            <Bell className="h-3 w-3" />
                            {event.reminder_minutes_before} min
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1 text-xs text-muted-foreground">
                            <Clock className="h-3 w-3" />
                            Sem lembrete
                          </span>
                        )}
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
