import { beforeEach, describe, expect, it, vi } from "vitest";
import { fireEvent, render, screen, userEvent, waitFor } from "@/test-utils";
import { server } from "@/mocks/server";
import { http, HttpResponse } from "msw";
import { CreateItemDialog } from "./CreateItemDialog";

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

const weddingUuid = "test-wedding-uuid";
const onOpenChange = vi.fn();
const onSuccess = vi.fn();

describe("CreateItemDialog", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders nothing when closed", () => {
    render(
      <CreateItemDialog
        weddingUuid={weddingUuid}
        open={false}
        onOpenChange={onOpenChange}
        onSuccess={onSuccess}
      />,
    );

    expect(screen.queryByText("Novo Item")).not.toBeInTheDocument();
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  });

  it("renders form fields when open", async () => {
    render(
      <CreateItemDialog
        weddingUuid={weddingUuid}
        open={true}
        onOpenChange={onOpenChange}
        onSuccess={onSuccess}
      />,
    );

    expect(screen.getByText("Novo Item")).toBeInTheDocument();
    expect(
      screen.getByText("Registre um item logístico vinculado ao evento."),
    ).toBeInTheDocument();

    expect(screen.getByLabelText("Nome")).toBeInTheDocument();
    expect(screen.getByLabelText("Descrição (Opcional)")).toBeInTheDocument();
    expect(screen.getByLabelText("Quantidade")).toBeInTheDocument();
    expect(
      screen.getByRole("combobox", { name: /status/i }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("combobox", { name: /contrato/i }),
    ).toBeInTheDocument();

    expect(
      screen.getByRole("button", { name: /criar item/i }),
    ).toBeInTheDocument();
  });

  it("fills form and submits", async () => {
    const user = userEvent.setup();

    let capturedBody: unknown;
    server.use(
      http.post("*/api/v1/logistics/items/", async ({ request }) => {
        capturedBody = await request.json();
        return HttpResponse.json({}, { status: 201 });
      }),
    );

    render(
      <CreateItemDialog
        weddingUuid={weddingUuid}
        open={true}
        onOpenChange={onOpenChange}
        onSuccess={onSuccess}
      />,
    );

    await user.type(screen.getByLabelText("Nome"), "Item de Teste");
    await user.type(
      screen.getByLabelText("Descrição (Opcional)"),
      "Descrição detalhada do item",
    );

    const quantityInput = screen.getByLabelText("Quantidade");
    fireEvent.change(quantityInput, { target: { value: "3" } });

    await user.click(screen.getByRole("button", { name: /criar item/i }));

    await waitFor(() => {
      expect(capturedBody).toEqual({
        wedding: weddingUuid,
        name: "Item de Teste",
        description: "Descrição detalhada do item",
        quantity: 3,
        acquisition_status: "PENDING",
        contract: null,
      });
    });
  });

  it("shows success toast on successful create", async () => {
    const user = userEvent.setup();

    render(
      <CreateItemDialog
        weddingUuid={weddingUuid}
        open={true}
        onOpenChange={onOpenChange}
        onSuccess={onSuccess}
      />,
    );

    await user.type(screen.getByLabelText("Nome"), "Item");
    await user.click(screen.getByRole("button", { name: /criar item/i }));

    await waitFor(() => {
      expect(toastSuccess).toHaveBeenCalledWith("Item criado com sucesso!");
    });
  });

  it("calls onSuccess after successful create", async () => {
    const user = userEvent.setup();

    render(
      <CreateItemDialog
        weddingUuid={weddingUuid}
        open={true}
        onOpenChange={onOpenChange}
        onSuccess={onSuccess}
      />,
    );

    await user.type(screen.getByLabelText("Nome"), "Item");
    await user.click(screen.getByRole("button", { name: /criar item/i }));

    await waitFor(() => {
      expect(onSuccess).toHaveBeenCalled();
    });
  });

  it("shows error toast on API failure", async () => {
    server.use(
      http.post("*/api/v1/logistics/items/", () =>
        HttpResponse.json({ detail: "Erro ao criar item" }, { status: 500 }),
      ),
    );

    const user = userEvent.setup();

    render(
      <CreateItemDialog
        weddingUuid={weddingUuid}
        open={true}
        onOpenChange={onOpenChange}
        onSuccess={onSuccess}
      />,
    );

    await user.type(screen.getByLabelText("Nome"), "Item");
    await user.click(screen.getByRole("button", { name: /criar item/i }));

    await waitFor(
      () => {
        expect(toastError).toHaveBeenCalled();
      },
      { timeout: 5000 },
    );
  });
});
