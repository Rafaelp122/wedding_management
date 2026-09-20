import { useCallback, useMemo, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import {
  useSchedulerEventsList,
  getSchedulerEventsListQueryKey,
  useSchedulerSummaryGet,
  getSchedulerSummaryGetQueryKey,
} from "@/api/generated/v1/endpoints/scheduler/scheduler";
import { useWeddingsList } from "@/api/generated/v1/endpoints/weddings/weddings";
import type { EventOut } from "@/api/generated/v1/models/eventOut";
import { getPaginationInfo, usePagination } from "@/hooks/use-pagination";
import { mapSchedulerSummary } from "../utils/scheduler-helpers";

type ViewMode = "table" | "calendar";

/**
 * Hook principal para gerenciar o estado, dados e interações da página do cronograma (Scheduler).
 *
 * Consolida a listagem de eventos com paginação de servidor, resumo estatístico do backend,
 * modo de visualização (tabela/calendário) e opções de casamento para criação de eventos.
 *
 * @returns Estados compilados, dados calculados, paginação e manipuladores de eventos da página.
 */
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
  } = useSchedulerEventsList({
    limit: pagination.limit,
    offset: pagination.offset,
  });

  const {
    data: summaryResponse,
    isLoading: isLoadingSummary,
    error: summaryError,
  } = useSchedulerSummaryGet();

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

  const isLoading = isLoadingEvents || isLoadingWeddings || isLoadingSummary;
  const firstError = eventsError ?? summaryError ?? weddingsError;

  const summary = useMemo(
    () => mapSchedulerSummary(summaryResponse?.data),
    [summaryResponse],
  );

  const handleSelectEvent = useCallback((event: EventOut) => {
    setSelectedEvent(event);
    setEditDialogOpen(true);
  }, []);

  const handleEditSuccess = useCallback(() => {
    setEditDialogOpen(false);
    setSelectedEvent(null);
    queryClient.invalidateQueries({ queryKey: getSchedulerEventsListQueryKey() });
    queryClient.invalidateQueries({ queryKey: getSchedulerSummaryGetQueryKey() });
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
    queryClient.invalidateQueries({ queryKey: getSchedulerSummaryGetQueryKey() });
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
    paginationInfo,
    isLoading,
    firstError,
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
