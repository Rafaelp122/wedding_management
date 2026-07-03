import { describe, expect, it } from "vitest";
import { render, screen, userEvent, waitFor } from "@/test-utils";
import { TableRowActionsMenu } from "./table-row-actions-menu";

describe("TableRowActionsMenu", () => {
  it("renders with default label and shows tooltip on hover", async () => {
    const user = userEvent.setup();
    render(
      <TableRowActionsMenu>
        <div>Item 1</div>
      </TableRowActionsMenu>
    );

    const trigger = screen.getByRole("button", { name: /Abrir menu/i });
    expect(trigger).toBeInTheDocument();

    await user.hover(trigger);

    await waitFor(() => {
        expect(screen.getByRole("tooltip", { name: "Ações" })).toBeInTheDocument();
    });
  });

  it("renders with custom label and shows custom tooltip", async () => {
    const user = userEvent.setup();
    render(
      <TableRowActionsMenu label="Opções">
        <div>Item 1</div>
      </TableRowActionsMenu>
    );

    const trigger = screen.getByRole("button", { name: /Abrir menu/i });
    await user.hover(trigger);

    await waitFor(() => {
        expect(screen.getByRole("tooltip", { name: "Opções" })).toBeInTheDocument();
    });
  });
});
