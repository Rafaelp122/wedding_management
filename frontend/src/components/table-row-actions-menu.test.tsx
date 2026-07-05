import { describe, expect, it, vi } from "vitest";
import { render, screen, userEvent, waitFor } from "@/test-utils";
import { TableRowActionsMenu } from "./table-row-actions-menu";
import { DropdownMenuItem } from "@/components/ui/dropdown-menu";

describe("TableRowActionsMenu", () => {
  it("renders the menu with label and trigger tooltip", async () => {
    const label = "Custom Actions";
    const user = userEvent.setup();

    render(
      <TableRowActionsMenu label={label}>
        <DropdownMenuItem>Item 1</DropdownMenuItem>
      </TableRowActionsMenu>
    );

    const trigger = screen.getByRole("button", { name: label });
    expect(trigger).toBeInTheDocument();

    // Verify Tooltip
    await user.hover(trigger);
    await waitFor(() => {
      expect(screen.getByRole("tooltip", { name: label })).toBeInTheDocument();
    });

    // Open Menu
    await user.click(trigger);
    expect(screen.getByText(label, { selector: 'div' })).toBeInTheDocument();
    expect(screen.getByText("Item 1")).toBeInTheDocument();
  });

  it("calls onClick of children items", async () => {
    const onClick = vi.fn();
    const user = userEvent.setup();

    render(
      <TableRowActionsMenu>
        <DropdownMenuItem onClick={onClick}>Click Me</DropdownMenuItem>
      </TableRowActionsMenu>
    );

    await user.click(screen.getByRole("button", { name: /ações/i }));
    await user.click(screen.getByText("Click Me"));

    expect(onClick).toHaveBeenCalled();
  });
});
