import { useCallback, useMemo, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { useSchedulerEventsList, getSchedulerEventsListQueryKey } from "@/api/generated/v1/endpoints/scheduler/scheduler";
import { useWeddingsList } from "@/api/generated/v1/endpoints/weddings/weddings";
import { getApiErrorInfo } from "@/api/error-utils";
import type { EventOut } from "@/api/generated/v1/models/eventOut";
import { SchedulerEventsTable } from "../components/SchedulerEventsTable";
import { SchedulerCalendar } from "../components/SchedulerCalendar";
import { SchedulerSummaryCards } from "../components/SchedulerSummaryCards";
import { CreateEventDialog } from "../components/events/CreateEventDialog";
import { EditEventDialog } from "../components/events/EditEventDialog";

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { AlertCircle, CalendarIcon, Plus, TableIcon } from "lucide-react";

type ViewMode = "table" | "calendar";

export default function SchedulerPage() {
  const [viewMode, setViewMode] = useState<ViewMode>("table");
  const queryClient = useQueryClient();

  // Create event dialog state
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [createDefaultStart, setCreateDefaultStart] = useState<Date | undefined>();

  // Edit event dialog state
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [selectedEvent, setSelectedEvent] = useState<EventOut | null>(null);

  const EVENTS_PAGE_SIZE = 100;

  const [scheduleOffset, setScheduleOffset] = useState(0);

  const {
    data: eventsResponse,
    isLoading: isLoadingEvents,
    error: eventsError,
  } = useSchedulerEventsList({ limit: EVENTS_PAGE_SIZE, offset: scheduleOffset });
  const {
    data: weddingsResponse,
    isLoading: isLoadingWeddings,
    error: weddingsError,
  } = useWeddingsList({ limit: EVENTS_PAGE_SIZE });

  const events = useMemo(() => eventsResponse?.data.items ?? [], [eventsResponse]);
  const eventsCount = eventsResponse?.data.count ?? 0;
  const hasMoreEvents = scheduleOffset + EVENTS_PAGE_SIZE < eventsCount;
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

  // For the table: sorted events
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

  // Handlers
  const handleSelectEvent = useCallback((event: EventOut) => {
    setSelectedEvent(event);
    setEditDialogOpen(true);
  }, []);

  const handleEditSuccess = useCallback(() => {
    setEditDialogOpen(false);
    setSelectedEvent(null);
    queryClient.invalidateQueries({ queryKey: getSchedulerEventsListQueryKey({}) });
  }, [queryClient]);

  // Wedding options for the create event dialog (must be before handlers that use them)
  const weddingOptions = useMemo(
    () =>
      weddings.map((w) => ({
        uuid: w.uuid,
        label: `${w.bride_name} & ${w.groom_name}`,
      })),
    [weddings],
  );

  const defaultWeddingUuid = weddingOptions.length > 0
    ? weddingOptions[0].uuid
    : "";

  const handleSelectSlot = useCallback((startTime: Date) => {
    if (weddingOptions.length === 0) {
      toast.warning("Crie um casamento antes de adicionar eventos.");
      return;
    }
    setCreateDefaultStart(startTime);
    setCreateDialogOpen(true);
  }, [weddingOptions]);

  const handleCreateFromButton = useCallback(() => {
    if (weddingOptions.length === 0) {
      toast.warning("Crie um casamento antes de adicionar eventos.");
      return;
    }
    setCreateDefaultStart(undefined);
    setCreateDialogOpen(true);
  }, [weddingOptions]);

  const handleLoadMore = useCallback(() => {
    setScheduleOffset((prev) => prev + EVENTS_PAGE_SIZE);
  }, []);

  const handleCreateSuccess = useCallback(() => {
    setCreateDialogOpen(false);
    setCreateDefaultStart(undefined);
    queryClient.invalidateQueries({ queryKey: getSchedulerEventsListQueryKey({}) });
  }, [queryClient]);

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
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Scheduler</h2>
          <p className="text-muted-foreground">
            Visão global dos compromissos de todos os casamentos.
          </p>
        </div>

        {/* View toggle */}
        <div className="flex items-center gap-2">
          <Button
            variant="default"
            size="sm"
            onClick={handleCreateFromButton}
            className="gap-1.5"
          >
            <Plus className="h-4 w-4" />
            Novo Evento
          </Button>

          <div className="flex items-center gap-1 rounded-lg border p-1">
            <Button
              variant={viewMode === "table" ? "default" : "ghost"}
              size="sm"
              onClick={() => setViewMode("table")}
              className="gap-1.5"
            >
              <TableIcon className="h-4 w-4" />
              Tabela
            </Button>
            <Button
              variant={viewMode === "calendar" ? "default" : "ghost"}
              size="sm"
              onClick={() => setViewMode("calendar")}
              className="gap-1.5"
            >
              <CalendarIcon className="h-4 w-4" />
              Calendário
            </Button>
          </div>
        </div>
      </div>

      <SchedulerSummaryCards summary={summary} />

      {viewMode === "table" ? (
        <SchedulerEventsTable
          events={sortedEvents}
          weddingsByUuid={weddingsByUuid}
        />
      ) : (
        <SchedulerCalendar
          events={events}
          weddingsByUuid={weddingsByUuid}
          onSelectEvent={handleSelectEvent}
          onSelectSlot={handleSelectSlot}
        />
      )}

      {/* Create Event Dialog */}
      {defaultWeddingUuid && (
        <CreateEventDialog
          key={createDefaultStart?.getTime() ?? "no-date"}
          weddingUuid={defaultWeddingUuid}
          open={createDialogOpen}
          onOpenChange={setCreateDialogOpen}
          onSuccess={handleCreateSuccess}
          defaultStartTime={createDefaultStart}
          weddingOptions={weddingOptions}
        />
      )}

      {/* Edit Event Dialog */}
      {selectedEvent && (
        <EditEventDialog
          event={selectedEvent}
          open={editDialogOpen}
          onOpenChange={setEditDialogOpen}
          onSuccess={handleEditSuccess}
        />
      )}

      {/* Pagination */}
      {hasMoreEvents && (
        <div className="flex items-center justify-center gap-2 text-sm text-muted-foreground">
          <span>
            Mostrando {scheduleOffset + events.length} de {eventsCount} eventos
          </span>
          <Button variant="outline" size="sm" onClick={handleLoadMore}>
            Carregar mais
          </Button>
        </div>
      )}
    </div>
  );
}
