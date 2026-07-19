import { describe, expect, it, vi } from "vitest";
import { render, screen, userEvent } from "@/test-utils";
import { TableRowActionsMenu } from "./table-row-actions-menu";
import { DropdownMenuItem } from "@/components/ui/dropdown-menu";

describe("TableRowActionsMenu", () => {
  it("renders the trigger and label with default 'Ações' text", () => {
    render(
      <TableRowActionsMenu>
        <DropdownMenuItem>Ação 1</DropdownMenuItem>
      </TableRowActionsMenu>
    );

    // Assert that the trigger button is present
    expect(screen.getByRole("button")).toBeInTheDocument();
    expect(screen.getByText("Abrir menu")).toBeInTheDocument();

    // Assert that the default label is rendered
    expect(screen.getByText("Ações")).toBeInTheDocument();

    // Assert children are rendered
    expect(screen.getByText("Ação 1")).toBeInTheDocument();
  });

  it("renders the custom label when passed as prop", () => {
    render(
      <TableRowActionsMenu label="Opções de Item">
        <DropdownMenuItem>Ação 1</DropdownMenuItem>
      </TableRowActionsMenu>
    );

    expect(screen.getByText("Opções de Item")).toBeInTheDocument();
    expect(screen.queryByText("Ações")).not.toBeInTheDocument();
  });

  it("should support interaction when trigger and items are clicked", async () => {
    const user = userEvent.setup();
    const actionClickMock = vi.fn();

    render(
      <TableRowActionsMenu>
        <DropdownMenuItem onClick={actionClickMock}>Clique Aqui</DropdownMenuItem>
      </TableRowActionsMenu>
    );

    // Click trigger to open dropdown
    const trigger = screen.getByRole("button");
    await user.click(trigger);

    // Click the item
    const item = screen.getByText("Clique Aqui");
    await user.click(item);

    expect(actionClickMock).toHaveBeenCalledTimes(1);
  });
});
