import { describe, expect, it } from "vitest";
import { render, screen } from "@/test-utils";
import { WeddingVendorsTable } from "@/features/logistics/components/items/VendorsTable";
import { createMockContract } from "@/test-data";

describe("WeddingVendorsTable", () => {
  it("shows empty state when contracts array is empty", () => {
    render(<WeddingVendorsTable contracts={[]} />);

    expect(
      screen.getByText(/nenhum contrato de fornecedor/i),
    ).toBeInTheDocument();
  });

  it("renders contract rows with correct data", () => {
    const contract = createMockContract();
    render(<WeddingVendorsTable contracts={[contract]} />);

    // Supplier UUID prefix (first 8 chars of "supplier-uuid-123" = "supplier")
    expect(screen.getByText("supplier")).toBeInTheDocument();

    // Description
    expect(screen.getByText("Buffet contrato")).toBeInTheDocument();

    // Status badge
    expect(screen.getByText("ACTIVE")).toBeInTheDocument();

    // Formatted total amount (R$ with pt-BR decimal format)
    expect(screen.getByText(/R\$\s*5\.000,00/)).toBeInTheDocument();
  });

  it('shows "N/A" when signed_date is null/undefined', () => {
    render(
      <WeddingVendorsTable
        contracts={[createMockContract({ signed_date: undefined })]}
      />,
    );

    expect(screen.getByText("N/A")).toBeInTheDocument();
  });

  it("shows formatted date when signed_date is present", () => {
    render(
      <WeddingVendorsTable
        contracts={[createMockContract({ signed_date: "2025-01-15" })]}
      />,
    );

    expect(screen.getByText("15/01/2025")).toBeInTheDocument();
  });
});
