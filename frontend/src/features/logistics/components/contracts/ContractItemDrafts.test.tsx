import { describe, expect, it, vi, beforeEach } from "vitest";
import { render, screen, userEvent } from "@/test-utils";
import { ContractItemDrafts } from "@/features/logistics/components/contracts/ContractItemDrafts";
import type { ItemDraft } from "@/features/logistics/components/contracts/ContractItemDrafts";

describe("ContractItemDrafts", () => {
  const onDraftsChange = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders label and Adicionar button initially", () => {
    render(<ContractItemDrafts drafts={[]} onDraftsChange={onDraftsChange} />);

    expect(screen.getByText("Itens (Opcional)")).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /adicionar/i }),
    ).toBeInTheDocument();
  });

  it('shows "Nenhum item adicionado." when empty and form hidden', () => {
    render(<ContractItemDrafts drafts={[]} onDraftsChange={onDraftsChange} />);

    expect(screen.getByText("Nenhum item adicionado.")).toBeInTheDocument();
  });

  it("does not show empty state when form is visible", async () => {
    const user = userEvent.setup();
    render(<ContractItemDrafts drafts={[]} onDraftsChange={onDraftsChange} />);

    await user.click(screen.getByRole("button", { name: /adicionar/i }));

    expect(
      screen.queryByText("Nenhum item adicionado."),
    ).not.toBeInTheDocument();
  });

  it("shows inline form when Adicionar is clicked", async () => {
    const user = userEvent.setup();
    render(<ContractItemDrafts drafts={[]} onDraftsChange={onDraftsChange} />);

    await user.click(screen.getByRole("button", { name: /adicionar/i }));

    expect(screen.getByPlaceholderText("Nome do item")).toBeInTheDocument();
    expect(screen.getByDisplayValue("1")).toBeInTheDocument();
    expect(
      screen.getByRole("combobox", { name: "" }),
    ).toBeInTheDocument();
  });

  it("adds a draft when Confirm button is clicked and resets form", async () => {
    const user = userEvent.setup();
    render(<ContractItemDrafts drafts={[]} onDraftsChange={onDraftsChange} />);

    // Show form
    await user.click(screen.getByRole("button", { name: /adicionar/i }));

    // Fill name field
    const nameInput = screen.getByPlaceholderText("Nome do item");
    await user.type(nameInput, "Buffet Principal");

    // Click Confirm button (the button with no accessible name, i.e. the Check icon button)
    const buttons = screen.getAllByRole("button");
    const confirmButton = buttons.find(
      (b) => b.textContent?.includes("") && !b.textContent?.includes("Adicionar"),
    ) ?? buttons[buttons.length - 1];
    await user.click(confirmButton);

    expect(onDraftsChange).toHaveBeenCalledTimes(1);
    const newDrafts = onDraftsChange.mock.calls[0][0] as ItemDraft[];
    expect(newDrafts).toHaveLength(1);
    expect(newDrafts[0].name).toBe("Buffet Principal");
    expect(newDrafts[0].quantity).toBe(1);
    expect(newDrafts[0].acquisition_status).toBe("PENDING");
    expect(newDrafts[0].key).toBeDefined();

    // Form should be reset and hidden
    expect(
      screen.queryByPlaceholderText("Nome do item"),
    ).not.toBeInTheDocument();
  });

  it("adds a draft when Enter is pressed in the name field", async () => {
    const user = userEvent.setup();
    render(<ContractItemDrafts drafts={[]} onDraftsChange={onDraftsChange} />);

    await user.click(screen.getByRole("button", { name: /adicionar/i }));

    const nameInput = screen.getByPlaceholderText("Nome do item");
    await user.type(nameInput, "Mesa de Doces");
    await user.keyboard("{Enter}");

    expect(onDraftsChange).toHaveBeenCalledTimes(1);
    const newDrafts = onDraftsChange.mock.calls[0][0] as ItemDraft[];
    expect(newDrafts).toHaveLength(1);
    expect(newDrafts[0].name).toBe("Mesa de Doces");
  });

  it("displays added drafts with correct name, quantity, and status badge", async () => {
    const initialDrafts: ItemDraft[] = [
      {
        key: "existing-1",
        name: "Cadeiras",
        quantity: 50,
        acquisition_status: "PENDING",
      },
    ];

    const onDraftsChange = vi.fn();
    render(
      <ContractItemDrafts
        drafts={initialDrafts}
        onDraftsChange={onDraftsChange}
      />,
    );

    expect(screen.getByText("Cadeiras")).toBeInTheDocument();
    expect(screen.getByText("50")).toBeInTheDocument();
    expect(screen.getByText("Pendente")).toBeInTheDocument();
  });

  it("removes a draft when X button is clicked", async () => {
    const user = userEvent.setup();
    const initialDrafts: ItemDraft[] = [
      {
        key: "remove-me",
        name: "Buffet",
        quantity: 1,
        acquisition_status: "PENDING",
      },
    ];

    render(
      <ContractItemDrafts
        drafts={initialDrafts}
        onDraftsChange={onDraftsChange}
      />,
    );

    // The X button is inside each draft row — find the remove button by its icon
    const removeButton = screen.getByRole("button", { name: "" });
    await user.click(removeButton);

    expect(onDraftsChange).toHaveBeenCalledTimes(1);
    const updatedDrafts = onDraftsChange.mock.calls[0][0] as ItemDraft[];
    expect(updatedDrafts).toHaveLength(0);
  });

  it("does not add a draft with empty name", async () => {
    const user = userEvent.setup();
    render(<ContractItemDrafts drafts={[]} onDraftsChange={onDraftsChange} />);

    await user.click(screen.getByRole("button", { name: /adicionar/i }));

    // Click Confirm without filling the name
    const buttons = screen.getAllByRole("button");
    const confirmButton = buttons[buttons.length - 1];
    await user.click(confirmButton);

    expect(onDraftsChange).not.toHaveBeenCalled();
  });

  it("calls onDraftsChange with updated drafts after removing a draft from a populated list", async () => {
    const user = userEvent.setup();
    const existing: ItemDraft[] = [
      { key: "k1", name: "Item A", quantity: 2, acquisition_status: "PENDING" },
      { key: "k2", name: "Item B", quantity: 3, acquisition_status: "DONE" },
    ];

    const onChange = vi.fn();
    render(<ContractItemDrafts drafts={existing} onDraftsChange={onChange} />);

    // Find the X buttons inside draft rows
    // There are 2 X buttons + 1 "Adicionar" button = 3 total buttons
    const allButtons = screen.getAllByRole("button");
    // Filter out the Adicionar button to keep only the X (remove) buttons
    const removeButtons = allButtons.filter(
      (b) => !b.textContent?.includes("Adicionar"),
    );

    // Click the first X button to remove the first draft
    await user.click(removeButtons[0]);

    expect(onChange).toHaveBeenCalledTimes(1);
    const afterRemove = onChange.mock.calls[0][0] as ItemDraft[];
    expect(afterRemove).toHaveLength(1);
    expect(afterRemove[0].name).toBe("Item B");
  });

  it("calls onDraftsChange with correct drafts after adding a draft", async () => {
    const user = userEvent.setup();
    const onChange = vi.fn();
    render(<ContractItemDrafts drafts={[]} onDraftsChange={onChange} />);

    await user.click(screen.getByRole("button", { name: /adicionar/i }));
    const nameInput = screen.getByPlaceholderText("Nome do item");
    await user.type(nameInput, "Novo Item");
    await user.keyboard("{Enter}");

    expect(onChange).toHaveBeenCalledTimes(1);
    const newDrafts = onChange.mock.calls[0][0] as ItemDraft[];
    expect(newDrafts).toHaveLength(1);
    expect(newDrafts[0].name).toBe("Novo Item");
  });
});
