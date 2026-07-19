import { describe, expect, it, beforeEach } from "vitest";
import { render, screen, waitFor, server } from "@/test-utils";
import { http, HttpResponse } from "msw";
import { WeddingBudget } from "@/features/finances/components/budgets/Budget";

describe("WeddingBudget", () => {
  beforeEach(() => {
    server.use(
      http.get("*/api/v1/finances/budgets/for-wedding/:weddingUuid/", () =>
        HttpResponse.json({
          uuid: "b-1",
          wedding: "w-1",
          total_estimated: "50000.00",
          total_overall_spent: "25000.00",
          notes: "",
        }),
      ),
      http.get("*/api/v1/finances/categories/", () =>
        HttpResponse.json({
          items: [],
          count: 0,
        }),
      ),
    );
  });

  it("shows loading state initially", () => {
    server.use(
      http.get("*/api/v1/finances/budgets/for-wedding/:weddingUuid/", () => new Promise(() => {})),
    );

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
