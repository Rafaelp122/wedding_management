import { describe, expect, it } from "vitest";
import { render, screen } from "@/test-utils";
import { WeddingTimelineTable } from "@/features/scheduler/components/events/TimelineTable";
import { createMockEvent } from "@/test-data";

const mockEvents = [
  createMockEvent({ uuid: "e-1", title: "Reunião com noivos", event_type: "MEETING", start_time: "2025-06-15T10:00:00Z", location: "Escritório" }),
  createMockEvent({ uuid: "e-2", title: "Entrega das flores", event_type: "DELIVERY", start_time: "2025-06-15T14:00:00Z", location: null }),
];

describe("WeddingTimelineTable", () => {
  it("shows empty state when no events", () => {
    render(<WeddingTimelineTable events={[]} />);

    expect(
      screen.getByText(/nenhum evento registrado/i),
    ).toBeInTheDocument();
  });

  it("renders event rows", () => {
    render(<WeddingTimelineTable events={mockEvents} />);

    expect(screen.getByText("Reunião com noivos")).toBeInTheDocument();
    expect(screen.getByText("Entrega das flores")).toBeInTheDocument();
  });

  it("shows N/A for null location", () => {
    render(<WeddingTimelineTable events={mockEvents} />);

    expect(screen.getByText("N/A")).toBeInTheDocument();
  });

  it("renders event type badges", () => {
    render(<WeddingTimelineTable events={mockEvents} />);

    expect(screen.getByText("MEETING")).toBeInTheDocument();
    expect(screen.getByText("DELIVERY")).toBeInTheDocument();
  });
});
