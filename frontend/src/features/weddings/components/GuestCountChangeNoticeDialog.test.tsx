import { describe, expect, it, vi } from "vitest";
import { render, screen, userEvent } from "@/test-utils";
import { GuestCountChangeNoticeDialog } from "./GuestCountChangeNoticeDialog";

describe("GuestCountChangeNoticeDialog", () => {
  it("renders notice dialog with updated counts when open", () => {
    render(
      <GuestCountChangeNoticeDialog
        open={true}
        onOpenChange={vi.fn()}
        previousGuestCount={150}
        newGuestCount={200}
      />,
    );

    expect(
      screen.getByText("Alteração no Número de Convidados"),
    ).toBeInTheDocument();
    expect(screen.getByText("150")).toBeInTheDocument();
    expect(screen.getByText("200")).toBeInTheDocument();
    expect(
      screen.getByText(/análise de impacto em fornecedores sensíveis à contagem/i),
    ).toBeInTheDocument();
  });

  it("calls onConfirm and onOpenChange when clicking Entendido", async () => {
    const onOpenChange = vi.fn();
    const onConfirm = vi.fn();
    const user = userEvent.setup();

    render(
      <GuestCountChangeNoticeDialog
        open={true}
        onOpenChange={onOpenChange}
        previousGuestCount={100}
        newGuestCount={120}
        onConfirm={onConfirm}
      />,
    );

    await user.click(screen.getByRole("button", { name: "Entendido" }));

    expect(onOpenChange).toHaveBeenCalledWith(false);
    expect(onConfirm).toHaveBeenCalled();
  });

  it("renders generic message when counts are omitted", () => {
    render(
      <GuestCountChangeNoticeDialog
        open={true}
        onOpenChange={vi.fn()}
      />,
    );

    expect(
      screen.getByText(/a contagem estimada de convidados deste evento foi modificada/i),
    ).toBeInTheDocument();
  });

  it("does not render dialog content when open is false", () => {
    render(
      <GuestCountChangeNoticeDialog
        open={false}
        onOpenChange={vi.fn()}
      />,
    );

    expect(
      screen.queryByText("Alteração no Número de Convidados"),
    ).not.toBeInTheDocument();
  });
});
