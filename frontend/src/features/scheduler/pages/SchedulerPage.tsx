import { useMemo } from "react";
import { useSchedulerAppointmentsList } from "@/api/generated/v1/endpoints/scheduler/scheduler";
import { useEventsListWeddings } from "@/api/generated/v1/endpoints/events/events";
import { getApiErrorInfo } from "@/api/error-utils";
import { SchedulerEventsTable } from "../components/SchedulerEventsTable";
import { SchedulerSummaryCards } from "../components/SchedulerSummaryCards";

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Skeleton } from "@/components/ui/skeleton";
import { AlertCircle } from "lucide-react";

export default function SchedulerPage() {
  const {
    data: eventsResponse,
    isLoading: isLoadingEvents,
    error: eventsError,
  } = useSchedulerAppointmentsList({ limit: 300 });
  const {
    data: weddingsResponse,
    isLoading: isLoadingWeddings,
    error: weddingsError,
  } = useEventsListWeddings({ limit: 200 });

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
          `${wedding.wedding_detail?.groom_name} & ${wedding.wedding_detail?.bride_name}`,
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

    return {
      total: events.length,
      upcoming,
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
      "Não foi possível carregar o scheduler.",
    );

    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertTitle>Erro ao carregar scheduler</AlertTitle>
        <AlertDescription>{message}</AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      <div>
        <h2 className="text-3xl font-bold tracking-tight">Scheduler</h2>
        <p className="text-muted-foreground">
          Visão global dos compromissos de todos os casamentos.
        </p>
      </div>

      <SchedulerSummaryCards summary={summary} />
      <SchedulerEventsTable
        events={sortedEvents}
        weddingsByUuid={weddingsByUuid}
      />
    </div>
  );
}
