import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen, userEvent, waitFor, fireEvent } from "@/test-utils";
import { server } from "@/mocks/server";
import { CreateEventDialog } from "./CreateEventDialog";

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

describe("CreateEventDialog", () => {
  const onOpenChange = vi.fn();
  const onSuccess = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders the create event form", () => {
    render(
      <CreateEventDialog
        weddingUuid="wedding-1"
        open={true}
        onOpenChange={onOpenChange}
        onSuccess={onSuccess}
      />,
    );

    expect(screen.getByText("Novo Evento")).toBeInTheDocument();
    expect(screen.getByLabelText("Título")).toBeInTheDocument();
    expect(screen.getByLabelText("Data/Hora Início *")).toBeInTheDocument();
    expect(screen.getByText("Criar Evento")).toBeInTheDocument();
  });

  it("does not offer pagamento as an event type option", () => {
    render(
      <CreateEventDialog
        weddingUuid="wedding-1"
        open={true}
        onOpenChange={onOpenChange}
        onSuccess={onSuccess}
      />,
    );

    // BR-S01: EVENT_TYPE_OPTIONS no longer includes "pagamento"
    // The Select shows the selected value as text, which is "Reunião" by default
    // "Pagamento" should not appear anywhere in the rendered dialog
    expect(
      screen.queryByText("Pagamento"),
    ).not.toBeInTheDocument();
  });

  it("renders recurrence field", () => {
    render(
      <CreateEventDialog
        weddingUuid="wedding-1"
        open={true}
        onOpenChange={onOpenChange}
        onSuccess={onSuccess}
      />,
    );

    expect(screen.getByText("Recorrência")).toBeInTheDocument();
  });

  it("renders reminder checkbox", () => {
    render(
      <CreateEventDialog
        weddingUuid="wedding-1"
        open={true}
        onOpenChange={onOpenChange}
        onSuccess={onSuccess}
      />,
    );

    expect(screen.getByText("Ativar Lembrete")).toBeInTheDocument();
  });

  it("does not render when closed", () => {
    render(
      <CreateEventDialog
        weddingUuid="wedding-1"
        open={false}
        onOpenChange={onOpenChange}
        onSuccess={onSuccess}
      />,
    );

    expect(screen.queryByText("Novo Evento")).not.toBeInTheDocument();
  });

  it("submits form and shows success toast", async () => {
    const { http, HttpResponse } = await import("msw");
    server.use(
      http.post("*/api/v1/events/", () =>
        HttpResponse.json({ uuid: "new-ev", title: "Novo Evento" }, { status: 201 }),
      ),
    );

    render(
      <CreateEventDialog
        weddingUuid="wedding-1"
        open={true}
        onOpenChange={onOpenChange}
        onSuccess={onSuccess}
      />,
    );

    await userEvent.type(screen.getByLabelText("Título"), "Minha Reunião");

    const startInput = screen.getByLabelText("Data/Hora Início *");
    fireEvent.change(startInput, { target: { value: "2026-08-15T09:00" } });

    await userEvent.click(screen.getByRole("button", { name: /criar evento/i }));

    await waitFor(() => {
      expect(toastSuccess).toHaveBeenCalled();
    });
    expect(onSuccess).toHaveBeenCalled();
  });
});
