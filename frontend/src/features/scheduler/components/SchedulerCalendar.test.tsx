import { describe, expect, it, vi } from "vitest";
import { render, screen, userEvent } from "@/test-utils";
import { SchedulerCalendar } from "./SchedulerCalendar";
import { createMockEvent } from "@/test-data";
import type { EventOut } from "@/api/generated/v1/models/eventOut";

describe("SchedulerCalendar", () => {
  const mockEvents: EventOut[] = [
    createMockEvent({
      uuid: "ev-1",
      title: "Reunião com Buffet",
      event_type: "reuniao",
      start_time: "2026-06-15T09:00:00Z",
    }),
  ];

  const weddingsByUuid = new Map([
    ["wedding-1", "Casamento Silva & Souza"],
  ]);

  const onSelectEvent = vi.fn();
  const onSelectSlot = vi.fn();

  it("renders without crashing", () => {
    render(
      <SchedulerCalendar
        events={mockEvents}
        weddingsByUuid={weddingsByUuid}
        onSelectEvent={onSelectEvent}
        onSelectSlot={onSelectSlot}
      />,
    );

    expect(screen.getByText("Mês")).toBeInTheDocument();
  });

  it("renders toolbar navigation (Month view)", () => {
    render(
      <SchedulerCalendar
        events={mockEvents}
        weddingsByUuid={weddingsByUuid}
        onSelectEvent={onSelectEvent}
        onSelectSlot={onSelectSlot}
      />,
    );

    expect(screen.getByText("Mês")).toBeInTheDocument();
    expect(screen.getByText("Hoje")).toBeInTheDocument();
  });

  it("renders without errors when no events provided", () => {
    render(
      <SchedulerCalendar
        events={[]}
        weddingsByUuid={new Map()}
        onSelectEvent={onSelectEvent}
        onSelectSlot={onSelectSlot}
      />,
    );

    expect(screen.getByText("Mês")).toBeInTheDocument();
  });

  it("changes calendar views and navigates dates", async () => {
    const user = userEvent.setup();
    render(
      <SchedulerCalendar
        events={[]}
        weddingsByUuid={new Map()}
        onSelectEvent={onSelectEvent}
        onSelectSlot={onSelectSlot}
      />,
    );

    await user.click(screen.getByRole("button", { name: "Semana" }));
    expect(screen.getByRole("button", { name: "Semana" })).toHaveClass("rbc-active");

    await user.click(screen.getByRole("button", { name: "Agenda" }));
    expect(screen.getByRole("button", { name: "Agenda" })).toHaveClass("rbc-active");

    await user.click(screen.getByRole("button", { name: "Próximo" }));
    await user.click(screen.getByRole("button", { name: "Anterior" }));
  });

  it("renders and selects an event in the current month", async () => {
    const user = userEvent.setup();
    const currentEvent = createMockEvent({
      uuid: "current-event",
      wedding: "wedding-without-label",
      title: "Evento de hoje",
      start_time: new Date().toISOString(),
      end_time: undefined,
      location: null,
      event_type: "tipo-desconhecido",
    });
    const selectEvent = vi.fn();

    render(
      <SchedulerCalendar
        events={[currentEvent]}
        weddingsByUuid={new Map()}
        onSelectEvent={selectEvent}
        onSelectSlot={onSelectSlot}
      />,
    );

    await user.click(screen.getByText(/Evento de hoje \(wedding-/));
    expect(selectEvent).toHaveBeenCalledWith(currentEvent);
  });

});
