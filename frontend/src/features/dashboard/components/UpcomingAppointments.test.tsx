import { describe, expect, it } from "vitest";
import { render, screen, waitFor } from "@/test-utils";
import { UpcomingAppointments } from "@/features/dashboard/components/UpcomingAppointments";
import { server } from "@/mocks/server";
import { http, HttpResponse } from "msw";

describe("UpcomingAppointments", () => {
  it("renders header title", () => {
    render(<UpcomingAppointments />);
    expect(screen.getByText("Agenda")).toBeInTheDocument();
  });

  it("has a link to scheduler page when no weddingUuid", () => {
    render(<UpcomingAppointments />);
    const link = screen.getByRole("link", { name: /ver calendário/i });
    expect(link).toHaveAttribute("href", "/scheduler");
  });

  it("has a link to wedding timeline when weddingUuid is provided", () => {
    const uuid = "abc-123";
    render(<UpcomingAppointments weddingUuid={uuid} />);
    const link = screen.getByRole("link", { name: /ver calendário/i });
    expect(link).toHaveAttribute(
      "href",
      `/weddings/${uuid}?tab=planning&subtab=timeline`,
    );
  });

  it("shows loading skeletons initially", () => {
    render(<UpcomingAppointments />);
    const skeletons = document.querySelectorAll("[class*='animate-pulse']");
    expect(skeletons.length).toBeGreaterThan(0);
  });

  it("shows empty state when no upcoming events", async () => {
    server.use(
      http.get("*/api/v1/scheduler/events/", () =>
        HttpResponse.json({ items: [], count: 0, limit: 5, offset: 0 }),
      ),
    );

    render(<UpcomingAppointments />);

    await waitFor(() => {
      expect(
        screen.getByText("Nenhum evento próximo."),
      ).toBeInTheDocument();
    });
  });

  it("shows wedding-specific empty state when weddingUuid is provided", async () => {
    server.use(
      http.get("*/api/v1/scheduler/events/", () =>
        HttpResponse.json({ items: [], count: 0, limit: 5, offset: 0 }),
      ),
    );

    render(<UpcomingAppointments weddingUuid="abc-123" />);

    await waitFor(() => {
      expect(
        screen.getByText("Nenhum evento agendado para este casamento."),
      ).toBeInTheDocument();
    });
  });

  it("filters past events, sorts upcoming events, and limits the list", async () => {
    const future = Date.now() + 86_400_000;
    const events = Array.from({ length: 7 }, (_, index) => ({
      uuid: `future-${index}`,
      company_id: "company-1",
      wedding: "wedding-1",
      title: `Evento ${index}`,
      description: index === 0 ? "Descricao do evento" : null,
      event_type: "reuniao",
      start_time: new Date(future + index * 3_600_000).toISOString(),
      recurrence_rule: "none",
      reminder_enabled: false,
      reminder_minutes_before: 30,
    }));

    server.use(
      http.get("*/api/v1/scheduler/events/", () =>
        HttpResponse.json({
          items: [
            events[6],
            ...events.slice(0, 6),
            { ...events[0], uuid: "past", title: "Evento passado", start_time: "2020-01-01T10:00:00Z" },
          ],
          count: 8,
        }),
      ),
    );

    render(<UpcomingAppointments />);

    await waitFor(() => expect(screen.getByText("Evento 0")).toBeInTheDocument());
    expect(screen.getByText("Descricao do evento")).toBeInTheDocument();
    expect(screen.getByText("Evento 4")).toBeInTheDocument();
    expect(screen.queryByText("Evento 5")).not.toBeInTheDocument();
    expect(screen.queryByText("Evento passado")).not.toBeInTheDocument();
  });

  it("sends the wedding filter to the API", async () => {
    let requestedWedding: string | null = null;
    server.use(
      http.get("*/api/v1/scheduler/events/", ({ request }) => {
        requestedWedding = new URL(request.url).searchParams.get("wedding_id");
        return HttpResponse.json({ items: [], count: 0 });
      }),
    );

    render(<UpcomingAppointments weddingUuid="wedding-123" />);

    await waitFor(() => expect(requestedWedding).toBe("wedding-123"));
  });
});
