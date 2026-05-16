import { describe, expect, it, vi } from "vitest";
import { render, screen, userEvent, waitFor } from "@/test-utils";
import { CreateWeddingDialog } from "@/features/weddings/components/CreateWeddingDialog";
import { server } from "@/mocks/server";

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

describe("CreateWeddingDialog", () => {
  it("renders nothing when closed", () => {
    render(
      <CreateWeddingDialog
        open={false}
        onOpenChange={vi.fn()}
        onSuccess={vi.fn()}
      />,
    );

    expect(
      screen.queryByText("Novo Casamento"),
    ).not.toBeInTheDocument();
  });

  it("renders dialog when open", () => {
    render(
      <CreateWeddingDialog
        open={true}
        onOpenChange={vi.fn()}
        onSuccess={vi.fn()}
      />,
    );

    expect(screen.getByText("Novo Casamento")).toBeInTheDocument();
  });

  it("renders form fields", () => {
    render(
      <CreateWeddingDialog
        open={true}
        onOpenChange={vi.fn()}
        onSuccess={vi.fn()}
      />,
    );

    expect(screen.getByLabelText("Nome do Noivo")).toBeInTheDocument();
    expect(screen.getByLabelText("Nome da Noiva")).toBeInTheDocument();
    expect(screen.getByLabelText("Local")).toBeInTheDocument();
    expect(screen.getByLabelText("Data do Casamento")).toBeInTheDocument();
  });

  it("calls onOpenChange when cancel is clicked", async () => {
    const onOpenChange = vi.fn();
    render(
      <CreateWeddingDialog
        open={true}
        onOpenChange={onOpenChange}
        onSuccess={vi.fn()}
      />,
    );

    const user = userEvent.setup();
    await user.click(screen.getByRole("button", { name: /cancelar/i }));
    expect(onOpenChange).toHaveBeenCalledWith(false);
  });

  it("submits form and calls onSuccess", async () => {
    const onSuccess = vi.fn();
    render(
      <CreateWeddingDialog
        open={true}
        onOpenChange={vi.fn()}
        onSuccess={onSuccess}
      />,
    );

    const user = userEvent.setup();
    await user.type(screen.getByLabelText("Nome do Noivo"), "João");
    await user.type(screen.getByLabelText("Nome da Noiva"), "Maria");
    await user.type(screen.getByLabelText("Local"), "Salão");
    await user.type(screen.getByLabelText("Data do Casamento"), "2025-12-25");
    await user.click(screen.getByRole("button", { name: /criar casamento/i }));

    await waitFor(
      () => {
        expect(toastSuccess).toHaveBeenCalledWith(
          "Casamento criado com sucesso!",
        );
        expect(onSuccess).toHaveBeenCalled();
      },
      { timeout: 5000 },
    );
  });

  it("shows validation error for empty fields", async () => {
    render(
      <CreateWeddingDialog
        open={true}
        onOpenChange={vi.fn()}
        onSuccess={vi.fn()}
      />,
    );

    const user = userEvent.setup();
    await user.click(screen.getByRole("button", { name: /criar casamento/i }));

    await screen.findByText(/invalid/i);
  });

  it("shows error toast on API failure", async () => {
    const { http, HttpResponse } = await import("msw");
    server.use(
      http.post("*/api/v1/weddings/", () =>
        HttpResponse.json({ detail: "Erro interno" }, { status: 500 }),
      ),
    );

    render(
      <CreateWeddingDialog
        open={true}
        onOpenChange={vi.fn()}
        onSuccess={vi.fn()}
      />,
    );

    const user = userEvent.setup();
    await user.type(screen.getByLabelText("Nome do Noivo"), "João");
    await user.type(screen.getByLabelText("Nome da Noiva"), "Maria");
    await user.type(screen.getByLabelText("Local"), "Salão");
    await user.type(screen.getByLabelText("Data do Casamento"), "2025-12-25");
    await user.click(screen.getByRole("button", { name: /criar casamento/i }));

    await waitFor(
      () => {
        expect(toastError).toHaveBeenCalledWith("Erro interno");
      },
      { timeout: 5000 },
    );
  });
});
