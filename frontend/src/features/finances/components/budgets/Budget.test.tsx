import { describe, expect, it } from "vitest";
import { render, screen, waitFor } from "@/test-utils";
import { WeddingBudget } from "@/features/finances/components/budgets/Budget";

describe("WeddingBudget", () => {
  it("shows loading state initially", () => {
    render(<WeddingBudget weddingUuid="w-1" />);

    const skeletons = document.querySelectorAll("[class*='animate-pulse']");
    expect(skeletons.length).toBeGreaterThan(0);
  });

  it("renders budget summary after loading", async () => {
    render(<WeddingBudget weddingUuid="w-1" />);

    await waitFor(() => {
      expect(
        screen.getByText(/orçamento total/i),
      ).toBeInTheDocument();
    });
  });

  it("renders categories card after loading", async () => {
    render(<WeddingBudget weddingUuid="w-1" />);

    await waitFor(() => {
      expect(
        screen.getByText(/categorias de custo/i),
      ).toBeInTheDocument();
    });
  });
});
