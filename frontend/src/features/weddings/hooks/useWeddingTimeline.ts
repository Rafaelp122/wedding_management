import { useSchedulerEventsList } from "@/api/generated/v1/endpoints/scheduler/scheduler";

export function useWeddingTimeline(weddingUuid: string) {
  const {
    data: eventsResponse,
    isLoading,
    error,
  } = useSchedulerEventsList({ wedding_id: weddingUuid });

  const events = eventsResponse?.data?.items || [];

  return {
    events,
    isLoading,
    error,
  };
}
