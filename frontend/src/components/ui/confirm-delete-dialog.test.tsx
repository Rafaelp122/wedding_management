import { describe, expect, it, vi } from "vitest";
import { render, screen, userEvent } from "@/test-utils";
import { ConfirmDeleteDialog } from "@/components/ui/confirm-delete-dialog";

const defaultProps = {
  open: true,
  onOpenChange: vi.fn(),
  title: "Deletar Casamento",
  description: "Tem certeza que deseja deletar este casamento?",
  itemName: "Casamento do João",
  onConfirm: vi.fn(),
};

describe("ConfirmDeleteDialog", () => {
  it("renders title, description, and itemName", () => {
    render(
      <ConfirmDeleteDialog
        {...defaultProps}
        requireTypedConfirmation
      />,
    );

    expect(
      screen.getByRole("heading", { name: /deletar casamento/i }),
    ).toBeInTheDocument();
    expect(
      screen.getByText(/tem certeza que deseja deletar este casamento\?/i),
    ).toBeInTheDocument();
    expect(
      screen.getByText("Casamento do João"),
    ).toBeInTheDocument();
  });

  it("shows consequences list when provided", () => {
    const consequences = [
      "Todos os orçamentos serão perdidos",
      "Os convidados serão notificados",
    ];

    render(
      <ConfirmDeleteDialog
        {...defaultProps}
        consequences={consequences}
      />,
    );

    consequences.forEach((consequence) => {
      expect(screen.getByText(consequence)).toBeInTheDocument();
    });
  });

  it("shows typed confirmation input when requireTypedConfirmation=true", () => {
    render(
      <ConfirmDeleteDialog
        {...defaultProps}
        requireTypedConfirmation
      />,
    );

    expect(
      screen.getByPlaceholderText(/digite o nome aqui/i),
    ).toBeInTheDocument();
    expect(
      screen.getByText(/para confirmar, digite o nome:/i),
    ).toBeInTheDocument();
    // The itemName should be displayed in a styled box
    expect(
      screen.getByText("Casamento do João"),
    ).toBeInTheDocument();
  });

  it("confirm button disabled when typed text doesn't match itemName", () => {
    render(
      <ConfirmDeleteDialog
        {...defaultProps}
        requireTypedConfirmation
      />,
    );

    const confirmBtn = screen.getByRole("button", {
      name: /deletar permanentemente/i,
    });
    expect(confirmBtn).toBeDisabled();
  });

  it("confirm button enabled when typed text matches itemName", async () => {
    const user = userEvent.setup();

    render(
      <ConfirmDeleteDialog
        {...defaultProps}
        requireTypedConfirmation
      />,
    );

    const confirmBtn = screen.getByRole("button", {
      name: /deletar permanentemente/i,
    });
    expect(confirmBtn).toBeDisabled();

    const input = screen.getByPlaceholderText(/digite o nome aqui/i);
    await user.type(input, "Casamento do João");

    expect(confirmBtn).toBeEnabled();
  });

  it("confirm button always enabled when requireTypedConfirmation=false", () => {
    render(<ConfirmDeleteDialog {...defaultProps} />);

    const confirmBtn = screen.getByRole("button", {
      name: /deletar permanentemente/i,
    });
    expect(confirmBtn).toBeEnabled();
  });

  it("clicking confirm calls onConfirm", async () => {
    const onConfirm = vi.fn();
    const user = userEvent.setup();

    render(
      <ConfirmDeleteDialog
        {...defaultProps}
        onConfirm={onConfirm}
      />,
    );

    await user.click(
      screen.getByRole("button", { name: /deletar permanentemente/i }),
    );

    expect(onConfirm).toHaveBeenCalledTimes(1);
  });

  it("buttons disabled when isPending=true", () => {
    render(
      <ConfirmDeleteDialog
        {...defaultProps}
        isPending
      />,
    );

    const cancelBtn = screen.getByRole("button", { name: /cancelar/i });
    const confirmBtn = screen.getByRole("button", {
      name: /deletar permanentemente/i,
    });

    expect(cancelBtn).toBeDisabled();
    expect(confirmBtn).toBeDisabled();
  });

  it("clicking cancel calls onOpenChange(false)", async () => {
    const onOpenChange = vi.fn();
    const user = userEvent.setup();

    render(
      <ConfirmDeleteDialog
        {...defaultProps}
        onOpenChange={onOpenChange}
      />,
    );

    await user.click(
      screen.getByRole("button", { name: /cancelar/i }),
    );

    expect(onOpenChange).toHaveBeenCalledWith(false);
  });
});
