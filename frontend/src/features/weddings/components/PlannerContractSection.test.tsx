import { describe, expect, it, vi } from "vitest";
import { render, screen, userEvent } from "@/test-utils";
import { PlannerContractSection } from "./PlannerContractSection";
import { createMockPlannerContract } from "@/test-data";

describe("PlannerContractSection", () => {
  it("renders empty state when contract is null or undefined", async () => {
    const onEditContract = vi.fn();

    render(
      <PlannerContractSection
        contract={null}
        onEditContract={onEditContract}
      />,
    );

    expect(
      screen.getByText("Contrato da Assessoria"),
    ).toBeInTheDocument();
    expect(
      screen.getByText(/Nenhum contrato de honorários cadastrado/i),
    ).toBeInTheDocument();

    const defineButton = screen.getByRole("button", {
      name: /definir contrato/i,
    });
    expect(defineButton).toBeInTheDocument();

    const user = userEvent.setup();
    await user.click(defineButton);
    expect(onEditContract).toHaveBeenCalledTimes(1);
  });

  it("renders contract details correctly when contract is provided", async () => {
    const onEditContract = vi.fn();
    const mockContract = createMockPlannerContract({
      service_tier: "COMPLETA",
      effective_amount: "7500.00",
      installments_count: 5,
      signed_date: "2025-04-10",
      status: "SIGNED",
    });

    const { container } = render(
      <PlannerContractSection
        contract={mockContract}
        onEditContract={onEditContract}
      />,
    );

    expect(screen.getByText("Contrato de Assessoria")).toBeInTheDocument();
    expect(screen.getByText("Assessoria Completa")).toBeInTheDocument();
    expect(container.textContent).toContain("7.500");
    expect(screen.getByText("5 parcelas")).toBeInTheDocument();
    expect(screen.getByText("Assinado")).toBeInTheDocument();

    const editButton = screen.getByTitle("Editar contrato de assessoria");
    const user = userEvent.setup();
    await user.click(editButton);
    expect(onEditContract).toHaveBeenCalledTimes(1);
  });

  it("renders status Rascunho and 'Não assinado' when signed_date is null", () => {
    const mockContract = createMockPlannerContract({
      service_tier: "PARCIAL",
      effective_amount: "3000.00",
      installments_count: 1,
      signed_date: null,
      status: "DRAFT",
    });

    render(
      <PlannerContractSection
        contract={mockContract}
        onEditContract={vi.fn()}
      />,
    );

    expect(screen.getByText("Assessoria Parcial")).toBeInTheDocument();
    expect(screen.getByText("1 parcela")).toBeInTheDocument();
    expect(screen.getByText("Rascunho")).toBeInTheDocument();
    expect(screen.getByText("Não assinado")).toBeInTheDocument();
  });
});
