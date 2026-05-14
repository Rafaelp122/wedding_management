import { describe, expect, it } from "vitest";
import { render, screen, waitFor } from "@/test-utils";
import { WeddingExpensesTab } from "@/features/finances/components/expenses/ExpensesTab";

describe("WeddingExpensesTab", () => {
  it("shows loading state initially", () => {
    render(<WeddingExpensesTab weddingUuid="w-1" />);

    const skeletons = document.querySelectorAll("[class*='animate-pulse']");
    expect(skeletons.length).toBeGreaterThan(0);
  });

  it("renders expenses card after loading", async () => {
    render(<WeddingExpensesTab weddingUuid="w-1" />);

    await waitFor(() => {
      expect(
        screen.getByText(/despesas registradas/i),
      ).toBeInTheDocument();
    });
  });

  it("shows new expense button", async () => {
    render(<WeddingExpensesTab weddingUuid="w-1" />);

    await waitFor(() => {
      expect(
        screen.getByRole("button", { name: /nova despesa/i }),
      ).toBeInTheDocument();
    });
  });
});
