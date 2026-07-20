import { QueryClient } from "@tanstack/react-query";
import { HttpResponse, http } from "msw";
import { toast } from "sonner";
import { describe, expect, it, vi } from "vitest";
import { act, renderHook, server, waitFor } from "@/test-utils";
import { createMockEvent, createMockWedding } from "@/test-data";
import { useSchedulerPage } from "./useSchedulerPage";

const eventsUrl = "*/api/v1/scheduler/events/";
const weddingsUrl = "*/api/v1/weddings/";

describe("useSchedulerPage", () => {
  it("organizes API data for the page", async () => {
    const laterEvent = createMockEvent({
      uuid: "later",
      start_time: "2030-06-20T10:00:00Z",
      reminder_enabled: true,
    });
    const earlierEvent = createMockEvent({
      uuid: "earlier",
      start_time: "2030-06-10T10:00:00Z",
    });
    const wedding = createMockWedding({
      uuid: "w-1",
      bride_name: "Maria",
      groom_name: "Joao",
    });

    server.use(
      http.get(eventsUrl, () =>
        HttpResponse.json({ items: [laterEvent, earlierEvent], count: 2 }),
      ),
      http.get(weddingsUrl, () =>
        HttpResponse.json({ items: [wedding], count: 1 }),
      ),
    );

    const { result } = renderHook(() => useSchedulerPage());

    await waitFor(() => expect(result.current.isLoading).toBe(false));
    expect(result.current.events).toHaveLength(2);
    expect(result.current.paginatedEvents.map((event) => event.uuid)).toEqual([
      "earlier",
      "later",
    ]);
    expect(result.current.weddingsByUuid.get("w-1")).toBe("Joao & Maria");
    expect(result.current.weddingOptions).toEqual([
      { uuid: "w-1", label: "Maria & Joao" },
    ]);
    expect(result.current.defaultWeddingUuid).toBe("w-1");
    expect(result.current.summary).toMatchObject({ total: 2, withReminder: 1 });
    expect(result.current.paginationInfo.totalCount).toBe(2);
  });

  it("exposes the events error before the weddings error", async () => {
    server.use(
      http.get(eventsUrl, () => HttpResponse.json({}, { status: 500 })),
      http.get(weddingsUrl, () => HttpResponse.json({}, { status: 503 })),
    );

    const { result } = renderHook(() => useSchedulerPage());

    await waitFor(() => expect(result.current.isLoading).toBe(false));
    expect(result.current.firstError).toBeTruthy();
  });

  it("blocks event creation when there are no weddings", async () => {
    server.use(
      http.get(eventsUrl, () => HttpResponse.json({ items: [], count: 0 })),
      http.get(weddingsUrl, () => HttpResponse.json({ items: [], count: 0 })),
    );

    const { result } = renderHook(() => useSchedulerPage());
    await waitFor(() => expect(result.current.isLoading).toBe(false));

    act(() => result.current.handleCreateFromButton());
    act(() => result.current.handleSelectSlot(new Date("2030-01-01T12:00:00Z")));

    expect(toast.warning).toHaveBeenCalledTimes(2);
    expect(result.current.createDialogOpen).toBe(false);
    expect(result.current.defaultWeddingUuid).toBe("");
  });

  it("opens and resets create and edit flows", async () => {
    const event = createMockEvent();
    const wedding = createMockWedding();
    server.use(
      http.get(eventsUrl, () => HttpResponse.json({ items: [event], count: 1 })),
      http.get(weddingsUrl, () => HttpResponse.json({ items: [wedding], count: 1 })),
    );
    const queryClient = new QueryClient({
      defaultOptions: { queries: { retry: false } },
    });
    const invalidateQueries = vi.spyOn(queryClient, "invalidateQueries");
    const { result } = renderHook(() => useSchedulerPage(), { queryClient });
    await waitFor(() => expect(result.current.isLoading).toBe(false));

    const slotStart = new Date("2030-01-01T12:00:00Z");
    act(() => result.current.handleSelectSlot(slotStart));
    expect(result.current.createDialogOpen).toBe(true);
    expect(result.current.createDefaultStart).toEqual(slotStart);

    act(() => result.current.handleCreateSuccess());
    expect(result.current.createDialogOpen).toBe(false);
    expect(result.current.createDefaultStart).toBeUndefined();

    act(() => result.current.handleCreateFromButton());
    expect(result.current.createDialogOpen).toBe(true);
    expect(result.current.createDefaultStart).toBeUndefined();

    act(() => result.current.handleSelectEvent(event));
    expect(result.current.selectedEvent).toEqual(event);
    expect(result.current.editDialogOpen).toBe(true);

    act(() => result.current.handleEditSuccess());
    expect(result.current.selectedEvent).toBeNull();
    expect(result.current.editDialogOpen).toBe(false);
    expect(invalidateQueries).toHaveBeenCalledTimes(2);
  });
});
