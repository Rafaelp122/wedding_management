import { describe, expect, it } from "vitest";
import { render, screen } from "@/test-utils";
import { WeddingItemsTable } from "@/features/logistics/components/items/ItemsTable";
import { createMockItem } from "@/test-data";

describe("WeddingItemsTable", () => {
  it("shows empty state when no items", () => {
    render(<WeddingItemsTable items={[]} />);

    expect(
      screen.getByText(/nenhum item logístico/i),
    ).toBeInTheDocument();
  });

  it("renders item rows", () => {
    render(<WeddingItemsTable items={[createMockItem()]} />);

    expect(screen.getByText("Cadeiras")).toBeInTheDocument();
    expect(screen.getByText("Cadeiras Tiffany")).toBeInTheDocument();
    expect(screen.getByText("150")).toBeInTheDocument();
    expect(screen.getByText("PENDING")).toBeInTheDocument();
  });

  it("shows N/A for missing description", () => {
    render(
      <WeddingItemsTable
        items={[createMockItem({ description: "" })]}
      />,
    );

    expect(screen.getByText("N/A")).toBeInTheDocument();
  });
});
