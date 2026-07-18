import { useCallback, useMemo, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { useSchedulerEventsList, getSchedulerEventsListQueryKey } from "@/api/generated/v1/endpoints/scheduler/scheduler";
import { useWeddingsList } from "@/api/generated/v1/endpoints/weddings/weddings";
import type { EventOut } from "@/api/generated/v1/models/eventOut";
import { getPaginationInfo, usePagination } from "@/hooks/use-pagination";
import { sortEvents, paginateEvents, calculateSchedulerSummary } from "../utils/scheduler-helpers";

type ViewMode = "table" | "calendar";

export function useSchedulerPage() {
  const [viewMode, setViewMode] = useState<ViewMode>("table");
  const queryClient = useQueryClient();

  // Create event dialog state
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [createDefaultStart, setCreateDefaultStart] = useState<Date | undefined>();

  // Edit event dialog state
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [selectedEvent, setSelectedEvent] = useState<EventOut | null>(null);

  const WEDDINGS_PAGE_SIZE = 100;
  const pagination = usePagination(10);

  const {
    data: eventsResponse,
    isLoading: isLoadingEvents,
    error: eventsError,
  } = useSchedulerEventsList({ limit: 500, offset: 0 });

  const {
    data: weddingsResponse,
    isLoading: isLoadingWeddings,
    error: weddingsError,
  } = useWeddingsList({ limit: WEDDINGS_PAGE_SIZE });

  const events = useMemo(() => eventsResponse?.data.items ?? [], [eventsResponse]);
  const eventsCount = eventsResponse?.data.count ?? 0;
  const weddings = useMemo(
    () => weddingsResponse?.data.items ?? [],
    [weddingsResponse],
  );

  const paginationInfo = getPaginationInfo(
    pagination.page,
    pagination.pageSize,
    eventsCount,
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

  const sortedEvents = useMemo(() => sortEvents(events), [events]);

  const paginatedEvents = useMemo(
    () => paginateEvents(sortedEvents, pagination.offset, pagination.limit),
    [sortedEvents, pagination.offset, pagination.limit],
  );

  const summary = useMemo(() => calculateSchedulerSummary(events), [events]);

  const handleSelectEvent = useCallback((event: EventOut) => {
    setSelectedEvent(event);
    setEditDialogOpen(true);
  }, []);

  const handleEditSuccess = useCallback(() => {
    setEditDialogOpen(false);
    setSelectedEvent(null);
    queryClient.invalidateQueries({ queryKey: getSchedulerEventsListQueryKey() });
  }, [queryClient]);

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

  const handleCreateSuccess = useCallback(() => {
    setCreateDialogOpen(false);
    setCreateDefaultStart(undefined);
    queryClient.invalidateQueries({ queryKey: getSchedulerEventsListQueryKey() });
  }, [queryClient]);

  return {
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
  };
}
