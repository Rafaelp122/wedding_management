import { HttpResponse, http } from "msw";
import { toast } from "sonner";
import { describe, expect, it, vi } from "vitest";
import { act, renderHook, server, waitFor } from "@/test-utils";
import { createMockEvent } from "@/test-data";
import { useCreateEventForm } from "./useCreateEventForm";

const validEvent = {
  wedding: "wedding-1",
  title: "Reuniao",
  event_type: "reuniao",
  start_time: "2026-08-15T09:00:00.000Z",
  end_time: "2026-08-15T10:00:00.000Z",
  location: "Sala",
  description: "Alinhamento",
  recurrence_rule: "none",
  reminder_enabled: false,
  reminder_minutes_before: 60,
};

describe("useCreateEventForm", () => {
  it("uses the default start, resets on close, and submits converted dates", async () => {
    let body: unknown;
    server.use(
      http.post("*/api/v1/scheduler/events/", async ({ request }) => {
        body = await request.json();
        return HttpResponse.json(createMockEvent({ uuid: "created" }), { status: 201 });
      }),
    );
    const onOpenChange = vi.fn();
    const onSuccess = vi.fn();
    const defaultStartTime = new Date("2026-08-15T09:00:00Z");
    const { result } = renderHook(() =>
      useCreateEventForm({
        weddingUuid: "wedding-1",
        defaultStartTime,
        onOpenChange,
        onSuccess,
      }),
    );

    expect(result.current.form.getValues("start_time")).toBe(defaultStartTime.toISOString());
    act(() => result.current.handleOpenChange(true));
    act(() => result.current.handleOpenChange(false));
    expect(onOpenChange).toHaveBeenNthCalledWith(1, true);
    expect(onOpenChange).toHaveBeenNthCalledWith(2, false);

    act(() => result.current.onSubmit(validEvent));
    await waitFor(() => expect(onSuccess).toHaveBeenCalled());
    expect(body).toMatchObject({
      start_time: "2026-08-15T09:00:00Z",
      end_time: "2026-08-15T10:00:00Z",
    });
  });

  it("keeps an optional end null and reports API errors", async () => {
    let body: unknown;
    server.use(
      http.post("*/api/v1/scheduler/events/", async ({ request }) => {
        body = await request.json();
        return HttpResponse.json({ detail: "Falha ao criar" }, { status: 500 });
      }),
    );
    const { result } = renderHook(() =>
      useCreateEventForm({
        weddingUuid: "wedding-1",
        onOpenChange: vi.fn(),
        onSuccess: vi.fn(),
      }),
    );

    act(() => result.current.onSubmit({ ...validEvent, end_time: null }));

    await waitFor(() => expect(toast.error).toHaveBeenCalled());
    expect(body).toMatchObject({ end_time: null });
  });
});
