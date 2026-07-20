import { HttpResponse, http } from "msw";
import { toast } from "sonner";
import { describe, expect, it, vi } from "vitest";
import { act, renderHook, server, waitFor } from "@/test-utils";
import { createMockEvent } from "@/test-data";
import { useEditEventForm } from "./useEditEventForm";

describe("useEditEventForm", () => {
  it("resets when opened with another event and when closed", () => {
    const onOpenChange = vi.fn();
    const firstEvent = createMockEvent({ title: "Primeiro" });
    const secondEvent = createMockEvent({
      uuid: "event-2",
      title: "",
      location: null,
      description: null,
      end_time: null,
      recurrence_rule: "none",
    });
    let event = firstEvent;
    let open = false;
    const { result, rerender } = renderHook(() =>
      useEditEventForm({ event, open, onOpenChange, onSuccess: vi.fn() }),
    );

    event = secondEvent;
    open = true;
    rerender();
    expect(result.current.form.getValues()).toMatchObject({
      title: "",
      location: "",
      description: "",
      end_time: null,
    });

    act(() => result.current.handleOpenChange(true));
    act(() => result.current.handleOpenChange(false));
    expect(onOpenChange).toHaveBeenNthCalledWith(1, true);
    expect(onOpenChange).toHaveBeenNthCalledWith(2, false);
  });

  it("does not submit payment events", () => {
    let requests = 0;
    server.use(
      http.patch("*/api/v1/scheduler/events/:uuid/", () => {
        requests += 1;
        return HttpResponse.json(createMockEvent());
      }),
    );
    const paymentEvent = createMockEvent({ event_type: "pagamento" });
    const { result } = renderHook(() =>
      useEditEventForm({
        event: paymentEvent,
        open: true,
        onOpenChange: vi.fn(),
        onSuccess: vi.fn(),
      }),
    );

    act(() => result.current.onSubmit({
      location: "",
      description: "",
      start_time: null,
      end_time: null,
    }));
    expect(result.current.readOnly).toBe(true);
    expect(requests).toBe(0);
  });

  it("submits nullable dates and reports API errors", async () => {
    let body: unknown;
    server.use(
      http.patch("*/api/v1/scheduler/events/:uuid/", async ({ request }) => {
        body = await request.json();
        return HttpResponse.json({ detail: "Falha ao atualizar" }, { status: 500 });
      }),
    );
    const event = createMockEvent({ uuid: "event-1" });
    const { result } = renderHook(() =>
      useEditEventForm({
        event,
        open: true,
        onOpenChange: vi.fn(),
        onSuccess: vi.fn(),
      }),
    );

    act(() => result.current.onSubmit({
      location: "",
      description: "",
      start_time: null,
      end_time: null,
    }));

    await waitFor(() => expect(toast.error).toHaveBeenCalled());
    expect(body).toMatchObject({ start_time: null, end_time: null });
  });
});
