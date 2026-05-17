import { describe, expect, it, vi } from "vitest";
import { render, screen, userEvent } from "@/test-utils";
import { WeddingVendorsTable } from "@/features/logistics/components/items/VendorsTable";
import { createMockContract } from "@/test-data";

describe("WeddingVendorsTable", () => {
  it("shows empty state when no contracts", () => {
    render(<WeddingVendorsTable contracts={[]} />);

    expect(
      screen.getByText(/nenhum contrato de fornecedor/i),
    ).toBeInTheDocument();
  });

  it("renders contract rows with status badge and supplier name", () => {
    render(<WeddingVendorsTable contracts={[createMockContract()]} />);

    expect(screen.getByText("Assinado")).toBeInTheDocument();
    expect(screen.getByText("Buffet Gourmet Ltda")).toBeInTheDocument();
    expect(screen.getByText(/R\$\s*5\.?000/)).toBeInTheDocument();
  });

  it("shows N/A for missing signed date and description", () => {
    render(
      <WeddingVendorsTable
        contracts={[createMockContract({ signed_date: undefined, description: undefined })]}
      />,
    );

    const naValues = screen.getAllByText("N/A");
    expect(naValues.length).toBeGreaterThanOrEqual(2);
  });

  it("calls onDetail when a row is clicked", async () => {
    const onDetail = vi.fn();
    const contract = createMockContract();

    render(
      <WeddingVendorsTable
        contracts={[contract]}
        onDetail={onDetail}
      />,
    );

    const user = userEvent.setup();
    await user.click(screen.getByText("Assinado"));

    expect(onDetail).toHaveBeenCalledWith(contract.uuid);
  });

  it("renders addendum with indent when isAddendum returns true", () => {
    render(
      <WeddingVendorsTable
        contracts={[createMockContract()]}
        isAddendum={() => true}
      />,
    );

    expect(screen.getByText("↳ Aditivo")).toBeInTheDocument();
  });

  it("renders dropdown trigger when onEdit is provided", () => {
    const { container } = render(
      <WeddingVendorsTable
        contracts={[createMockContract()]}
        onEdit={vi.fn()}
      />,
    );

    const svg = container.querySelector("svg");
    expect(svg).toBeTruthy();
  });

  it("shows progress bar when contract has linked expense", () => {
    render(
      <WeddingVendorsTable
        contracts={[createMockContract({ has_linked_expense: true, progress_percent: 75 })]}
      />,
    );

    expect(screen.getByRole("progressbar")).toBeInTheDocument();
    expect(screen.getByText("75% pago")).toBeInTheDocument();
  });
});
