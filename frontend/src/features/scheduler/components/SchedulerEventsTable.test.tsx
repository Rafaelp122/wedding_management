import { describe, expect, it } from "vitest";
import { render, screen } from "@/test-utils";
import { SchedulerEventsTable } from "./SchedulerEventsTable";
import { createMockEvent } from "@/test-data";

const mockWeddingsMap = new Map<string, string>([
  ["w-1", "João & Maria"],
]);

describe("SchedulerEventsTable", () => {
  it("renders card title and description", () => {
    render(
      <SchedulerEventsTable events={[]} weddingsByUuid={new Map()} />,
    );

    expect(screen.getByText("Próximos compromissos")).toBeInTheDocument();
    expect(
      screen.getByText(
        "Eventos ordenados por data para facilitar o acompanhamento operacional.",
      ),
    ).toBeInTheDocument();
  });

  it("renders empty state when no events", () => {
    render(
      <SchedulerEventsTable events={[]} weddingsByUuid={new Map()} />,
    );

    expect(
      screen.getByText("Nenhum evento cadastrado até o momento."),
    ).toBeInTheDocument();
  });

  it("renders event rows with title and wedding name", () => {
    const events = [
      createMockEvent({
        uuid: "ev-1",
        title: "Reunião com fornecedor",
      }),
    ];
    render(
      <SchedulerEventsTable
        events={events}
        weddingsByUuid={mockWeddingsMap}
      />,
    );

    expect(screen.getByText("Reunião com fornecedor")).toBeInTheDocument();
    expect(screen.getByText("João & Maria")).toBeInTheDocument();
  });

  it("shows event type labels from EVENT_LABELS mapping", () => {
    const events = [
      createMockEvent({
        uuid: "ev-1",
        title: "Evento 1",
        event_type: "reuniao",
      }),
      createMockEvent({
        uuid: "ev-2",
        title: "Evento 2",
        event_type: "pagamento",
      }),
      createMockEvent({
        uuid: "ev-3",
        title: "Evento 3",
        event_type: "degustacao",
      }),
    ];
    render(
      <SchedulerEventsTable
        events={events}
        weddingsByUuid={mockWeddingsMap}
      />,
    );

    expect(screen.getByText("Reunião")).toBeInTheDocument();
    expect(screen.getByText("Pagamento")).toBeInTheDocument();
    expect(screen.getByText("Degustação")).toBeInTheDocument();
  });

  it("shows raw event_type as fallback when not in EVENT_LABELS", () => {
    const events = [
      createMockEvent({
        uuid: "ev-1",
        title: "Evento",
        event_type: "MEETING",
      }),
    ];
    render(
      <SchedulerEventsTable
        events={events}
        weddingsByUuid={mockWeddingsMap}
      />,
    );

    expect(screen.getByText("MEETING")).toBeInTheDocument();
  });

  it("shows reminder info with minutes when enabled", () => {
    const events = [
      createMockEvent({
        uuid: "ev-1",
        title: "Evento com lembrete",
        reminder_enabled: true,
        reminder_minutes_before: 30,
      }),
    ];
    render(
      <SchedulerEventsTable
        events={events}
        weddingsByUuid={mockWeddingsMap}
      />,
    );

    expect(screen.getByText("30 min")).toBeInTheDocument();
  });

  it('shows "Sem lembrete" when reminder is disabled', () => {
    const events = [
      createMockEvent({
        uuid: "ev-1",
        title: "Evento sem lembrete",
        reminder_enabled: false,
      }),
    ];
    render(
      <SchedulerEventsTable
        events={events}
        weddingsByUuid={mockWeddingsMap}
      />,
    );

    expect(screen.getByText("Sem lembrete")).toBeInTheDocument();
  });

  it("renders formatted start and end times via formatDateTimeBR", () => {
    const events = [
      createMockEvent({
        uuid: "ev-1",
        title: "Evento",
        start_time: "2025-06-15T10:00:00Z",
        end_time: "2025-06-15T12:00:00Z",
      }),
    ];
    render(
      <SchedulerEventsTable
        events={events}
        weddingsByUuid={mockWeddingsMap}
      />,
    );

    // formatDateTimeBR uses pt-BR locale with the system timezone (America/Sao_Paulo)
    expect(screen.getByText("15/06/2025, 07:00")).toBeInTheDocument();
    expect(screen.getByText("15/06/2025, 09:00")).toBeInTheDocument();
  });

  it("shows em dash when end_time is null", () => {
    const events = [
      createMockEvent({
        uuid: "ev-1",
        title: "Evento",
        start_time: "2025-06-15T10:00:00Z",
        end_time: null,
      }),
    ];
    render(
      <SchedulerEventsTable
        events={events}
        weddingsByUuid={mockWeddingsMap}
      />,
    );

    expect(screen.getByText("—")).toBeInTheDocument();
  });

  it("shows raw wedding UUID when wedding is not found in map", () => {
    const events = [
      createMockEvent({
        uuid: "ev-1",
        title: "Evento",
        wedding: "unknown-uuid",
      }),
    ];
    render(
      <SchedulerEventsTable
        events={events}
        weddingsByUuid={mockWeddingsMap}
      />,
    );

    expect(screen.getByText("unknown-uuid")).toBeInTheDocument();
  });
});
