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
});
