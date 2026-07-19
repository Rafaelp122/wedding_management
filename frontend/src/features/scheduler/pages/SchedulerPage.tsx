import { useSchedulerPage } from "../hooks/useSchedulerPage";
import { getApiErrorInfo } from "@/api/error-utils";
import { DataPagination } from "@/components/data-pagination";
import { SchedulerEventsTable } from "../components/SchedulerEventsTable";
import { SchedulerCalendar } from "../components/SchedulerCalendar";
import { SchedulerSummaryCards } from "../components/SchedulerSummaryCards";
import { CreateEventDialog } from "../components/events/CreateEventDialog";
import { EditEventDialog } from "../components/events/EditEventDialog";

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { AlertCircle, CalendarIcon, Plus, TableIcon } from "lucide-react";

export default function SchedulerPage() {
  const {
    viewMode,
    setViewMode,
    createDialogOpen,
    setCreateDialogOpen,
    createDefaultStart,
    editDialogOpen,
    setEditDialogOpen,
    selectedEvent,
    pagination,
    events,
    eventsCount,
    paginatedEvents,
    paginationInfo,
    isLoading,
    firstError,
    weddingsByUuid,
    summary,
    weddingOptions,
    defaultWeddingUuid,
    handleSelectEvent,
    handleEditSuccess,
    handleSelectSlot,
    handleCreateFromButton,
    handleCreateSuccess,
  } = useSchedulerPage();


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

      {isLoading ? (
        <>
          <div className="grid gap-4 md:grid-cols-3">
            <Skeleton className="h-28 w-full" />
            <Skeleton className="h-28 w-full" />
            <Skeleton className="h-28 w-full" />
          </div>
          <Skeleton className="h-96 w-full" />
        </>
      ) : (
        <>
          <SchedulerSummaryCards summary={summary} />

          {viewMode === "table" ? (
            <SchedulerEventsTable
              events={paginatedEvents}
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
        </>
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

      {viewMode === "table" && (
        <DataPagination
          from={paginationInfo.from}
          to={paginationInfo.to}
          totalCount={eventsCount}
          totalPages={paginationInfo.totalPages}
          currentPage={paginationInfo.page}
          hasPrevious={paginationInfo.hasPrevious}
          hasNext={paginationInfo.hasNext}
          onPrevious={pagination.previousPage}
          onNext={pagination.nextPage}
          onGoToPage={pagination.goToPage}
        />
      )}
    </div>
  );
}
