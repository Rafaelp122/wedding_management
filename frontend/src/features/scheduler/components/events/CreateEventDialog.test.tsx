import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen, userEvent, waitFor } from "@/test-utils";
import { server } from "@/mocks/server";
import { CreateEventDialog } from "./CreateEventDialog";
import { toast } from "sonner";

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

  it("shows the wedding selector only when multiple options exist", () => {
    const { rerender } = render(
      <CreateEventDialog
        weddingUuid="wedding-1"
        open={true}
        onOpenChange={onOpenChange}
        onSuccess={onSuccess}
        weddingOptions={[{ uuid: "wedding-1", label: "Maria & Joao" }]}
      />,
    );
    expect(screen.queryByText("Casamento")).not.toBeInTheDocument();

    rerender(
      <CreateEventDialog
        weddingUuid="wedding-1"
        open={true}
        onOpenChange={onOpenChange}
        onSuccess={onSuccess}
        weddingOptions={[
          { uuid: "wedding-1", label: "Maria & Joao" },
          { uuid: "wedding-2", label: "Ana & Luis" },
        ]}
      />,
    );
    expect(screen.getByText("Casamento")).toBeInTheDocument();
  });

  it("resets optional date and reminder inputs", async () => {
    render(
      <CreateEventDialog
        weddingUuid="wedding-1"
        open={true}
        onOpenChange={onOpenChange}
        onSuccess={onSuccess}
        defaultStartTime={new Date("2026-08-15T09:00:00Z")}
      />,
    );

    await userEvent.clear(screen.getByLabelText("Data/Hora Início *"));
    await userEvent.clear(screen.getByLabelText("Data/Hora Fim (opcional)"));
    await userEvent.clear(screen.getByLabelText("Minutos antes"));

    expect(screen.getByLabelText("Data/Hora Início *")).toHaveValue("");
    expect(screen.getByLabelText("Data/Hora Fim (opcional)")).toHaveValue("");
    expect(screen.getByLabelText("Minutos antes")).toHaveValue(60);
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
      http.post("*/api/v1/scheduler/events/", async ({ request }) => {
        expect(await request.json()).toEqual(
          expect.objectContaining({
            wedding: "wedding-1",
            title: "Minha Reunião",
            start_time: "2026-08-15T09:00:00Z",
          }),
        );
        return HttpResponse.json(
          { uuid: "new-ev", title: "Novo Evento" },
          { status: 201 },
        );
      }),
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
    await userEvent.type(startInput, "2026-08-15T09:00");

    await userEvent.click(screen.getByRole("button", { name: /criar evento/i }));

    await waitFor(() => {
      expect(toast.success).toHaveBeenCalled();
    });
    expect(onSuccess).toHaveBeenCalled();
  });

  it("shows validation error when end_time is before start_time", async () => {
    render(
      <CreateEventDialog
        weddingUuid="wedding-1"
        open={true}
        onOpenChange={onOpenChange}
        onSuccess={onSuccess}
      />,
    );

    await userEvent.type(screen.getByLabelText("Título"), "Test");

    const startInput = screen.getByLabelText("Data/Hora Início *");
    await userEvent.type(startInput, "2026-08-15T10:00");

    const endInput = screen.getByLabelText("Data/Hora Fim (opcional)");
    await userEvent.type(endInput, "2026-08-15T09:00");

    await userEvent.click(screen.getByRole("button", { name: /criar evento/i }));

    expect(
      await screen.findByText(
        "Data/hora de término deve ser posterior ao início.",
      ),
    ).toBeInTheDocument();
  });

  it("allows submission when end_time is after start_time", async () => {
    const { http, HttpResponse } = await import("msw");
    server.use(
      http.post("*/api/v1/scheduler/events/", async ({ request }) => {
        expect(await request.json()).toEqual(
          expect.objectContaining({
            start_time: "2026-08-15T09:00:00Z",
            end_time: "2026-08-15T10:00:00Z",
          }),
        );
        return HttpResponse.json(
          { uuid: "new-ev", title: "Test" },
          { status: 201 },
        );
      }),
    );

    render(
      <CreateEventDialog
        weddingUuid="wedding-1"
        open={true}
        onOpenChange={onOpenChange}
        onSuccess={onSuccess}
      />,
    );

    await userEvent.type(screen.getByLabelText("Título"), "Test");

    const startInput = screen.getByLabelText("Data/Hora Início *");
    await userEvent.type(startInput, "2026-08-15T09:00");

    const endInput = screen.getByLabelText("Data/Hora Fim (opcional)");
    await userEvent.type(endInput, "2026-08-15T10:00");

    await userEvent.click(screen.getByRole("button", { name: /criar evento/i }));

    await waitFor(() => {
      expect(toast.success).toHaveBeenCalled();
    });
    expect(onSuccess).toHaveBeenCalled();
  });

  it("allows submission when end_time is null (no validation needed)", async () => {
    const { http, HttpResponse } = await import("msw");
    server.use(
      http.post("*/api/v1/scheduler/events/", async ({ request }) => {
        expect(await request.json()).toEqual(
          expect.objectContaining({
            start_time: "2026-08-15T09:00:00Z",
            end_time: null,
          }),
        );
        return HttpResponse.json(
          { uuid: "new-ev", title: "Test" },
          { status: 201 },
        );
      }),
    );

    render(
      <CreateEventDialog
        weddingUuid="wedding-1"
        open={true}
        onOpenChange={onOpenChange}
        onSuccess={onSuccess}
      />,
    );

    await userEvent.type(screen.getByLabelText("Título"), "Test");

    const startInput = screen.getByLabelText("Data/Hora Início *");
    await userEvent.type(startInput, "2026-08-15T09:00");

    await userEvent.click(screen.getByRole("button", { name: /criar evento/i }));

    await waitFor(() => {
      expect(toast.success).toHaveBeenCalled();
    });
    expect(onSuccess).toHaveBeenCalled();
  });
});
