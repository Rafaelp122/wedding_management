import { describe, expect, it, vi } from "vitest";
import { render, screen, userEvent } from "@/test-utils";
import { WeddingFilters } from "@/features/weddings/components/WeddingFilters";

describe("WeddingFilters", () => {
  it("renders search input and status select", () => {
    render(
      <WeddingFilters
        search=""
        onSearchChange={vi.fn()}
        statusFilter="all"
        onStatusFilterChange={vi.fn()}
      />,
    );

    expect(
      screen.getByPlaceholderText(/buscar por noivos ou local/i),
    ).toBeInTheDocument();
    expect(screen.getByText("Todos os Status")).toBeInTheDocument();
  });

  it("calls onSearchChange when typing", async () => {
    const onSearchChange = vi.fn();
    render(
      <WeddingFilters
        search=""
        onSearchChange={onSearchChange}
        statusFilter="all"
        onStatusFilterChange={vi.fn()}
      />,
    );

    const user = userEvent.setup();
    await user.type(
      screen.getByPlaceholderText(/buscar por noivos ou local/i),
      "joão",
    );

    expect(onSearchChange).toHaveBeenCalled();
  });

  it("renders with initial search value", () => {
    render(
      <WeddingFilters
        search="maria"
        onSearchChange={vi.fn()}
        statusFilter="COMPLETED"
        onStatusFilterChange={vi.fn()}
      />,
    );

    expect(
      screen.getByPlaceholderText(/buscar por noivos ou local/i),
    ).toHaveValue("maria");
  });
});
