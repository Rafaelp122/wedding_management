import { describe, expect, it } from "vitest";
import { render, screen } from "@/test-utils";
import { WeddingVendorsTable } from "@/features/logistics/components/items/VendorsTable";
import { createMockContract } from "@/test-data";

describe("WeddingVendorsTable", () => {
  it("shows empty state when no contracts", () => {
    render(<WeddingVendorsTable contracts={[]} />);

    expect(
      screen.getByText(/nenhum contrato de fornecedor/i),
    ).toBeInTheDocument();
  });

  it("renders contract rows", () => {
    render(<WeddingVendorsTable contracts={[createMockContract()]} />);

    expect(screen.getByText("ACTIVE")).toBeInTheDocument();
    expect(screen.getByText("Buffet contrato")).toBeInTheDocument();
  });

  it("shows N/A for missing description", () => {
    render(
      <WeddingVendorsTable
        contracts={[createMockContract({ description: undefined, signed_date: undefined })]}
      />,
    );

    const naValues = screen.getAllByText("N/A");
    expect(naValues.length).toBeGreaterThanOrEqual(2);
  });
});
