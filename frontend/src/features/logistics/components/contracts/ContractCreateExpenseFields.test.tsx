import { describe, expect, it, vi, beforeAll, beforeEach } from "vitest";
import { render, screen, userEvent } from "@/test-utils";
import { ContractCreateExpenseFields } from "./ContractCreateExpenseFields";

// Polyfills for Radix UI Select in jsdom (missing browser APIs)
beforeAll(() => {
  Element.prototype.hasPointerCapture ??= () => false;
  Element.prototype.setPointerCapture ??= () => {};
  Element.prototype.releasePointerCapture ??= () => {};
  Element.prototype.scrollIntoView ??= () => {};
});

const mockCategories = [
  { uuid: "cat-1", name: "Decoração" },
  { uuid: "cat-2", name: "Buffet" },
  { uuid: "cat-3", name: "Música" },
];

function getTodayString(): string {
  return new Date().toISOString().slice(0, 10);
}

describe("ContractCreateExpenseFields", () => {
  const onExpenseChange = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders checkbox unchecked initially with correct label", () => {
    render(
      <ContractCreateExpenseFields
        categories={mockCategories}
        onExpenseChange={onExpenseChange}
      />,
    );

    const checkbox = screen.getByRole("checkbox", { name: /criar despesa/i });
    expect(checkbox).toBeInTheDocument();
    expect(checkbox).not.toBeChecked();
    expect(
      screen.getByText("Criar despesa a partir deste contrato"),
    ).toBeInTheDocument();
  });

  it("does not show category, installments, and date fields when unchecked", () => {
    render(
      <ContractCreateExpenseFields
        categories={mockCategories}
        onExpenseChange={onExpenseChange}
      />,
    );

    expect(screen.queryByText("Categoria da Despesa")).not.toBeInTheDocument();
    expect(screen.queryByText("Nº de Parcelas")).not.toBeInTheDocument();
    expect(screen.queryByText("Venc. 1ª Parcela")).not.toBeInTheDocument();
  });

  it("reveals additional fields when checkbox is checked", async () => {
    const user = userEvent.setup();
    render(
      <ContractCreateExpenseFields
        categories={mockCategories}
        onExpenseChange={onExpenseChange}
      />,
    );

    await user.click(screen.getByRole("checkbox", { name: /criar despesa/i }));

    expect(screen.getByText("Categoria da Despesa")).toBeInTheDocument();
    expect(screen.getByText("Nº de Parcelas")).toBeInTheDocument();
    expect(screen.getByText("Venc. 1ª Parcela")).toBeInTheDocument();
  });

  it("hides additional fields when checkbox is unchecked", async () => {
    const user = userEvent.setup();
    render(
      <ContractCreateExpenseFields
        categories={mockCategories}
        onExpenseChange={onExpenseChange}
      />,
    );

    const checkbox = screen.getByRole("checkbox", { name: /criar despesa/i });

    await user.click(checkbox);
    expect(screen.getByText("Categoria da Despesa")).toBeInTheDocument();

    await user.click(checkbox);
    expect(screen.queryByText("Categoria da Despesa")).not.toBeInTheDocument();
    expect(screen.queryByText("Nº de Parcelas")).not.toBeInTheDocument();
    expect(screen.queryByText("Venc. 1ª Parcela")).not.toBeInTheDocument();
  });

  it("selecting a category calls onExpenseChange with correct uuid", async () => {
    const user = userEvent.setup();
    render(
      <ContractCreateExpenseFields
        categories={mockCategories}
        onExpenseChange={onExpenseChange}
      />,
    );

    await user.click(screen.getByRole("checkbox", { name: /criar despesa/i }));
    onExpenseChange.mockClear();

    await user.click(screen.getByRole("combobox"));
    const option = await screen.findByRole("option", { name: "Decoração" });
    await user.click(option);

    expect(onExpenseChange).toHaveBeenCalledWith(
      expect.objectContaining({ category: "cat-1" }),
    );
  });

  it("changing installments calls onExpenseChange with correct value", async () => {
    const user = userEvent.setup();
    render(
      <ContractCreateExpenseFields
        categories={mockCategories}
        onExpenseChange={onExpenseChange}
      />,
    );

    await user.click(screen.getByRole("checkbox", { name: /criar despesa/i }));
    onExpenseChange.mockClear();

    const input = screen.getByDisplayValue("1");
    await user.type(input, "5", {
      initialSelectionStart: 0,
      initialSelectionEnd: 1,
    });

    expect(onExpenseChange).toHaveBeenCalledWith(
      expect.objectContaining({ numInstallments: 5 }),
    );
  });

  it("clamps numInstallments to min 1", async () => {
    const user = userEvent.setup();
    render(
      <ContractCreateExpenseFields
        categories={mockCategories}
        onExpenseChange={onExpenseChange}
      />,
    );

    await user.click(screen.getByRole("checkbox", { name: /criar despesa/i }));
    onExpenseChange.mockClear();

    const input = screen.getByDisplayValue("1");
    await user.type(input, "-3", {
      initialSelectionStart: 0,
      initialSelectionEnd: 1,
    });

    expect(onExpenseChange).toHaveBeenCalledWith(
      expect.objectContaining({ numInstallments: 1 }),
    );
  });

  it("changing date calls onExpenseChange with correct date string", async () => {
    const user = userEvent.setup();
    render(
      <ContractCreateExpenseFields
        categories={mockCategories}
        onExpenseChange={onExpenseChange}
      />,
    );

    await user.click(screen.getByRole("checkbox", { name: /criar despesa/i }));
    onExpenseChange.mockClear();

    const dateInput = screen.getByDisplayValue(getTodayString());
    await user.clear(dateInput);
    await user.type(dateInput, "2026-06-15");

    expect(onExpenseChange).toHaveBeenCalledWith(
      expect.objectContaining({ firstDueDate: "2026-06-15" }),
    );
  });

  it("onExpenseChange receives correct checked value when toggling", async () => {
    const user = userEvent.setup();
    render(
      <ContractCreateExpenseFields
        categories={mockCategories}
        onExpenseChange={onExpenseChange}
      />,
    );

    await user.click(screen.getByRole("checkbox", { name: /criar despesa/i }));
    expect(onExpenseChange).toHaveBeenCalledWith(
      expect.objectContaining({ checked: true }),
    );

    onExpenseChange.mockClear();

    await user.click(screen.getByRole("checkbox", { name: /criar despesa/i }));
    expect(onExpenseChange).toHaveBeenCalledWith(
      expect.objectContaining({ checked: false }),
    );
  });
});
