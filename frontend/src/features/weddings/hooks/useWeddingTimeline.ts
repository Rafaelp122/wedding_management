import { useSchedulerAppointmentsList } from "@/api/generated/v1/endpoints/scheduler/scheduler";

export function useWeddingTimeline(weddingUuid: string) {
  const {
    data: eventsResponse,
    isLoading,
    error,
  } = useSchedulerAppointmentsList({ event_id: weddingUuid });

  const events = eventsResponse?.data?.items || [];

  return {
    events,
    isLoading,
    error,
  };
}
