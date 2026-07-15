import { describe, expect, it, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@/test-utils";
import { WeddingBudget } from "@/features/finances/components/budgets/Budget";
import { useWeddingBudget } from "../../hooks/useBudget";

const defaultMockState = {
  budget: {} as any,
  categories: [],
  isLoading: false,
  budgetError: null,
  isEditing: false,
  editTotal: "",
  isSaving: false,
  totalEstimated: 50000,
  totalAllocated: 30000,
  totalSpent: 25000,
  progressPercentage: 50,
  progressColor: "bg-green-500",
  setEditTotal: vi.fn(),
  handleEditInit: vi.fn(),
  handleSave: vi.fn(),
  handleCancelEdit: vi.fn(),
};

describe("WeddingBudget", () => {
  beforeEach(() => {
    vi.mocked(useWeddingBudget).mockReturnValue(defaultMockState);
  });

  it("shows loading state initially", () => {
    vi.mocked(useWeddingBudget).mockReturnValue({
      ...defaultMockState,
      isLoading: true,
    });

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
