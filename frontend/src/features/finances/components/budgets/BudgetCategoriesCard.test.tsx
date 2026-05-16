import { describe, expect, it } from "vitest";
import { render, screen } from "@/test-utils";
import { WeddingBudgetCategoriesCard } from "@/features/finances/components/budgets/BudgetCategoriesCard";
import { createMockBudgetCategory } from "@/test-data";

describe("WeddingBudgetCategoriesCard", () => {
  it("shows empty state when no categories", () => {
    render(<WeddingBudgetCategoriesCard categories={[]} />);

    expect(
      screen.getByText(/nenhuma categoria encontrada/i),
    ).toBeInTheDocument();
  });

  it("renders categories table", () => {
    const categories = [
      createMockBudgetCategory({ uuid: "c-1", name: "Buffet", description: "Comida e bebidas" }),
      createMockBudgetCategory({ uuid: "c-2", name: "Decoração", description: null }),
    ];

    render(<WeddingBudgetCategoriesCard categories={categories} />);

    expect(screen.getByText("Categorias de Custo")).toBeInTheDocument();
    expect(screen.getByText("Buffet")).toBeInTheDocument();
    expect(screen.getByText("Decoração")).toBeInTheDocument();
    expect(screen.getByText("Comida e bebidas")).toBeInTheDocument();
    expect(screen.getByText("N/A")).toBeInTheDocument();
  });
});
