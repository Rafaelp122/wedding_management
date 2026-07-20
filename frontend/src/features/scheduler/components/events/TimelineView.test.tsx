import { describe, expect, it, vi } from "vitest";
vi.unmock("@/features/scheduler/components/events/TimelineView");
import { render, screen, userEvent, waitFor } from "@/test-utils";
import { WeddingTimelineTab } from "./TimelineView";
import { server } from "@/mocks/server";
import { http, HttpResponse } from "msw";

describe("WeddingTimelineTab (TimelineView)", () => {
  const weddingUuid = "wedding-123";

  it("shows loading state initially", () => {
    server.use(
      http.get("*/api/v1/scheduler/events/", async () => {
        await new Promise(() => {});
        return HttpResponse.json({ items: [], count: 0 });
      })
    );

    render(<WeddingTimelineTab weddingUuid={weddingUuid} />);
    const skeletons = document.querySelectorAll("[class*='animate-pulse']");
    expect(skeletons.length).toBeGreaterThan(0);
  });

  it("shows error state when API fails", async () => {
    server.use(
      http.get("*/api/v1/scheduler/events/", () => {
        return HttpResponse.json({ detail: "Error" }, { status: 500 });
      })
    );

    render(<WeddingTimelineTab weddingUuid={weddingUuid} />);

    await waitFor(() => {
      expect(
        screen.getByText("Não foi possível carregar o cronograma deste casamento.")
      ).toBeInTheDocument();
    });
  });

  it("renders events table and allows opening CreateEventDialog", async () => {
    const mockEvent = {
      uuid: "event-1",
      title: "Reunião de Alinhamento",
      event_type: "REUNIAO",
      event_date: "2026-09-20",
      start_time: "14:00",
      end_time: "15:00",
      location: "Fazenda Vila Rica",
      status: "AGENDADO",
    };

    server.use(
      http.get("*/api/v1/scheduler/events/", () => {
        return HttpResponse.json({ items: [mockEvent], count: 1 });
      })
    );

    render(<WeddingTimelineTab weddingUuid={weddingUuid} />);

    await waitFor(() => {
      expect(screen.getByText("Cronograma de Eventos")).toBeInTheDocument();
      expect(screen.getByText("Reunião de Alinhamento")).toBeInTheDocument();
    });

    const user = userEvent.setup();
    const newBtn = screen.getByRole("button", { name: /novo evento/i });
    await user.click(newBtn);

    expect(await screen.findByRole("heading", { name: /novo evento/i })).toBeInTheDocument();
  });
});
