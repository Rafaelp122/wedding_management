import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen, userEvent, waitFor } from "@/test-utils";
import { server } from "@/mocks/server";
import { http, HttpResponse } from "msw";
import { toast } from "sonner";
import { CreateTaskDialog } from "./CreateTaskDialog";

const weddingUuid = "test-wedding-uuid";
const onOpenChange = vi.fn();
const onSuccess = vi.fn();

describe("CreateTaskDialog", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders nothing when closed", () => {
    render(
      <CreateTaskDialog
        weddingUuid={weddingUuid}
        open={false}
        onOpenChange={onOpenChange}
        onSuccess={onSuccess}
      />,
    );

    expect(screen.queryByText("Novo Item de Checklist")).not.toBeInTheDocument();
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  });

  it("renders form fields when open", () => {
    render(
      <CreateTaskDialog
        weddingUuid={weddingUuid}
        open={true}
        onOpenChange={onOpenChange}
        onSuccess={onSuccess}
      />,
    );

    expect(screen.getByText("Novo Item de Checklist")).toBeInTheDocument();
    expect(
      screen.getByText("Cadastre uma tarefa no cronograma operacional do casamento."),
    ).toBeInTheDocument();

    expect(screen.getByLabelText("Título")).toBeInTheDocument();
    expect(screen.getByRole("combobox", { name: /prioridade/i })).toBeInTheDocument();
    expect(screen.getByLabelText(/prazo/i)).toBeInTheDocument();
    expect(screen.getByLabelText("Descrição (Opcional)")).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /criar tarefa/i }),
    ).toBeInTheDocument();
  });

  it("fills form and submits task", async () => {
    const user = userEvent.setup();
    let capturedBody: unknown;

    server.use(
      http.post("*/api/v1/scheduler/tasks/", async ({ request }) => {
        capturedBody = await request.json();
        return HttpResponse.json(
          {
            uuid: "task-created-uuid",
            company_id: "comp-1",
            wedding: weddingUuid,
            title: "Comprar lembrancinhas",
            description: "Comprar 200 caixinhas",
            priority: "HIGH",
            due_date: "2026-11-20",
            is_completed: false,
          },
          { status: 201 },
        );
      }),
    );

    render(
      <CreateTaskDialog
        weddingUuid={weddingUuid}
        open={true}
        onOpenChange={onOpenChange}
        onSuccess={onSuccess}
      />,
    );

    await user.type(screen.getByLabelText("Título"), "Comprar lembrancinhas");
    await user.type(
      screen.getByLabelText("Descrição (Opcional)"),
      "Comprar 200 caixinhas",
    );

    // Open Priority select and select "Alta"
    const prioritySelect = screen.getByRole("combobox", { name: /prioridade/i });
    await user.click(prioritySelect);
    const highOption = await screen.findByRole("option", { name: "Alta" });
    await user.click(highOption);

    // Fill date
    const dateInput = screen.getByLabelText(/prazo/i);
    await user.type(dateInput, "2026-11-20");

    await user.click(screen.getByRole("button", { name: /criar tarefa/i }));

    await waitFor(() => {
      expect(capturedBody).toEqual(
        expect.objectContaining({
          wedding: weddingUuid,
          title: "Comprar lembrancinhas",
          description: "Comprar 200 caixinhas",
          priority: "HIGH",
          due_date: "2026-11-20",
          is_completed: false,
        }),
      );
    });

    await waitFor(() => {
      expect(toast.success).toHaveBeenCalledWith("Item de checklist criado com sucesso!");
      expect(onSuccess).toHaveBeenCalled();
      expect(onOpenChange).toHaveBeenCalledWith(false);
    });
  });

  it("shows error toast on API failure", async () => {
    server.use(
      http.post("*/api/v1/scheduler/tasks/", () =>
        HttpResponse.json({ detail: "Erro interno" }, { status: 500 }),
      ),
    );

    const user = userEvent.setup();

    render(
      <CreateTaskDialog
        weddingUuid={weddingUuid}
        open={true}
        onOpenChange={onOpenChange}
        onSuccess={onSuccess}
      />,
    );

    await user.type(screen.getByLabelText("Título"), "Tarefa com erro");
    await user.click(screen.getByRole("button", { name: /criar tarefa/i }));

    await waitFor(() => {
      expect(toast.error).toHaveBeenCalled();
    });
  });
});
