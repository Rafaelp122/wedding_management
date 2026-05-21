import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen, userEvent, waitFor } from "@/test-utils";
import { server } from "@/mocks/server";
import { EditEventDialog } from "./EditEventDialog";
import { createMockEvent } from "@/test-data";
import type { EventOut } from "@/api/generated/v1/models/eventOut";

const { toastSuccess, toastError } = vi.hoisted(() => ({
  toastSuccess: vi.fn(),
  toastError: vi.fn(),
}));

vi.mock("sonner", async (importOriginal) => {
  const actual = await importOriginal<typeof import("sonner")>();
  return {
    ...actual,
    toast: {
      ...actual.toast,
      success: toastSuccess,
      error: toastError,
    },
  };
});

describe("EditEventDialog", () => {
  const onOpenChange = vi.fn();
  const onSuccess = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("Payment events (read-only)", () => {
    const paymentEvent: EventOut = createMockEvent({
      uuid: "ev-pay-1",
      title: "Pagamento: Buffet - Parcela 1/3",
      event_type: "pagamento",
      start_time: "2026-07-01T09:00:00Z",
    }) as EventOut;

    it("renders read-only view for PAYMENT events", () => {
      render(
        <EditEventDialog
          event={paymentEvent}
          open={true}
          onOpenChange={onOpenChange}
          onSuccess={onSuccess}
        />,
      );

      expect(screen.getByText("Detalhes do Evento")).toBeInTheDocument();
      expect(screen.getByText("Evento somente leitura")).toBeInTheDocument();
    });

    it("displays event data as text (not form fields)", () => {
      render(
        <EditEventDialog
          event={paymentEvent}
          open={true}
          onOpenChange={onOpenChange}
          onSuccess={onSuccess}
        />,
      );

      expect(
        screen.getByText("Pagamento: Buffet - Parcela 1/3"),
      ).toBeInTheDocument();
      expect(screen.getByText("Pagamento")).toBeInTheDocument();
    });

    it("shows Fechar button (not Salvar)", () => {
      render(
        <EditEventDialog
          event={paymentEvent}
          open={true}
          onOpenChange={onOpenChange}
          onSuccess={onSuccess}
        />,
      );

      expect(screen.getByText("Fechar")).toBeInTheDocument();
      expect(
        screen.queryByText("Salvar Alterações"),
      ).not.toBeInTheDocument();
    });

    it("does not show edit form controls", () => {
      render(
        <EditEventDialog
          event={paymentEvent}
          open={true}
          onOpenChange={onOpenChange}
          onSuccess={onSuccess}
        />,
      );

      expect(
        screen.queryByLabelText("Título"),
      ).not.toBeInTheDocument();
    });
  });

  describe("Non-payment events (editable)", () => {
    const meetingEvent: EventOut = createMockEvent({
      uuid: "ev-mtg-1",
      title: "Reunião com Buffet",
      event_type: "reuniao",
      start_time: "2026-08-01T10:00:00Z",
      recurrence_rule: "none",
    }) as EventOut;

    it("renders edit form for non-PAYMENT events", () => {
      render(
        <EditEventDialog
          event={meetingEvent}
          open={true}
          onOpenChange={onOpenChange}
          onSuccess={onSuccess}
        />,
      );

      expect(screen.getByText("Editar Evento")).toBeInTheDocument();
      expect(screen.getByLabelText("Título")).toBeInTheDocument();
      expect(screen.getByText("Salvar Alterações")).toBeInTheDocument();
    });

    it("pre-fills title field with event data", () => {
      render(
        <EditEventDialog
          event={meetingEvent}
          open={true}
          onOpenChange={onOpenChange}
          onSuccess={onSuccess}
        />,
      );

      const titleInput = screen.getByLabelText("Título");
      expect(titleInput).toHaveValue("Reunião com Buffet");
    });

    it("submits update and shows success toast", async () => {
      const { http, HttpResponse } = await import("msw");
      server.use(
        http.patch("*/api/v1/events/ev-mtg-1/", () =>
          HttpResponse.json(
            { uuid: "ev-mtg-1", title: "Reunião Atualizada", event_type: "reuniao" },
            { status: 200 },
          ),
        ),
      );

      render(
        <EditEventDialog
          event={meetingEvent}
          open={true}
          onOpenChange={onOpenChange}
          onSuccess={onSuccess}
        />,
      );

      await userEvent.clear(screen.getByLabelText("Título"));
      await userEvent.type(screen.getByLabelText("Título"), "Reunião Atualizada");
      await userEvent.click(screen.getByRole("button", { name: /salvar/i }));

      await waitFor(() => {
        expect(toastSuccess).toHaveBeenCalled();
      });
      expect(onSuccess).toHaveBeenCalled();
    });

    it("does not render when closed", () => {
      render(
        <EditEventDialog
          event={meetingEvent}
          open={false}
          onOpenChange={onOpenChange}
          onSuccess={onSuccess}
        />,
      );

      expect(screen.queryByText("Editar Evento")).not.toBeInTheDocument();
    });
  });
});
