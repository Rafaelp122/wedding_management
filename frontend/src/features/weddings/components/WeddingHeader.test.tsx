import { describe, expect, it, vi } from "vitest";
import { render, screen, userEvent } from "@/test-utils";
import { WeddingHeader } from "./WeddingHeader";
import { createMockWedding } from "@/test-data";

const mockWedding = createMockWedding({
  groom_name: "João",
  bride_name: "Maria",
  location: "Fazenda Vila Rica",
  expected_guests: 150,
  total_budget: 75000,
  template: "beach_6m",
  status: "IN_PROGRESS",
});

describe("WeddingHeader", () => {
  it("renders names, template, location and guests info", () => {
    const onEditClick = vi.fn();
    render(
      <WeddingHeader
        wedding={mockWedding}
        displayDate="15 Set 2026"
        checklistPercentage={45}
        onEditClick={onEditClick}
      />
    );

    expect(screen.getByText("João & Maria")).toBeInTheDocument();
    expect(screen.getByText("Campestre")).toBeInTheDocument(); // beach_6m mapping
    expect(screen.getByText("Fazenda Vila Rica")).toBeInTheDocument();
    expect(screen.getByText("150 Convidados")).toBeInTheDocument();
    expect(screen.getByText("15 Set 2026")).toBeInTheDocument();
  });

  it("renders budget and checklist percentage", () => {
    const onEditClick = vi.fn();
    render(
      <WeddingHeader
        wedding={mockWedding}
        displayDate="15 Set 2026"
        checklistPercentage={45}
        onEditClick={onEditClick}
      />
    );

    expect(screen.getByText("R$ 75k")).toBeInTheDocument();
    expect(screen.getByText("45%")).toBeInTheDocument();
  });

  it("calls onEditClick callback when edit button is clicked", async () => {
    const onEditClick = vi.fn();
    render(
      <WeddingHeader
        wedding={mockWedding}
        displayDate="15 Set 2026"
        checklistPercentage={45}
        onEditClick={onEditClick}
      />
    );

    const editBtn = screen.getByTitle("Editar dados do casamento");
    await userEvent.click(editBtn);

    expect(onEditClick).toHaveBeenCalledTimes(1);
  });
});
