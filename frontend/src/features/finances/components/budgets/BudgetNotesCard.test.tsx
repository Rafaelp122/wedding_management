import { describe, expect, it } from "vitest";
import { render, screen } from "@/test-utils";
import { WeddingBudgetNotesCard } from "@/features/finances/components/budgets/BudgetNotesCard";

describe("WeddingBudgetNotesCard", () => {
  it("renders the card title", () => {
    render(<WeddingBudgetNotesCard notes="Some notes" />);

    expect(screen.getByText("Observações Globais")).toBeInTheDocument();
  });

  it("renders notes text when provided", () => {
    render(<WeddingBudgetNotesCard notes="Comprar flores para o buquê" />);

    expect(
      screen.getByText("Comprar flores para o buquê"),
    ).toBeInTheDocument();
  });

  it("renders the card structure even when notes is empty", () => {
    render(<WeddingBudgetNotesCard notes="" />);

    expect(screen.getByText("Observações Globais")).toBeInTheDocument();
    expect(screen.getByRole("heading", { level: 3 })).toBeInTheDocument();
  });

  it("preserves whitespace in notes", () => {
    const notes = "Linha 1\n\nLinha 2\n- Item 3";
    render(<WeddingBudgetNotesCard notes={notes} />);

    expect(screen.getByText(/Linha 1/)).toBeInTheDocument();
    expect(screen.getByText(/Linha 2/)).toBeInTheDocument();
    expect(screen.getByText(/- Item 3/)).toBeInTheDocument();
  });
});
