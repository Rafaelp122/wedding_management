import { describe, expect, it, vi } from "vitest";
import { render, screen, userEvent, waitFor } from "@/test-utils";
import { ConvertToPlanningDialog } from "./ConvertToPlanningDialog";
import { toast } from "sonner";
import { createMockWedding, createMockPlannerContract } from "@/test-data";

describe("ConvertToPlanningDialog", () => {
  it("renders warning and disables submit when wedding has no contract", () => {
    const weddingWithoutContract = createMockWedding({
      status: "PROPOSAL",
      planner_contract: null,
    });

    render(
      <ConvertToPlanningDialog
        wedding={weddingWithoutContract}
        open={true}
        onOpenChange={vi.fn()}
      />,
    );

    expect(
      screen.getByText("Contrato da assessoria obrigatório"),
    ).toBeInTheDocument();
    const convertBtn = screen.getByRole("button", {
      name: /efetivar casamento/i,
    });
    expect(convertBtn).toBeDisabled();
  });

  it("renders summary when wedding has planner contract", () => {
    const contract = createMockPlannerContract({
      service_tier: "COMPLETA",
      effective_amount: "8000.00",
      installments_count: 4,
    });

    const weddingWithContract = createMockWedding({
      groom_name: "Gabriel",
      bride_name: "Mariana",
      status: "PROPOSAL",
      planner_contract: contract,
    });

    render(
      <ConvertToPlanningDialog
        wedding={weddingWithContract}
        open={true}
        onOpenChange={vi.fn()}
      />,
    );

    expect(screen.getByText("Resumo da Contratação")).toBeInTheDocument();
    expect(screen.getByText(/Gabriel & Mariana/)).toBeInTheDocument();
    expect(screen.getByText("Assessoria Completa")).toBeInTheDocument();
    expect(screen.getByText(/8\.000/)).toBeInTheDocument();
  });

  it("calls conversion endpoint and shows success toast when submitted", async () => {
    const contract = createMockPlannerContract({
      service_tier: "COMPLETA",
      effective_amount: "5000.00",
    });

    const wedding = createMockWedding({
      status: "PROPOSAL",
      planner_contract: contract,
    });

    const onSuccess = vi.fn();
    const onOpenChange = vi.fn();

    render(
      <ConvertToPlanningDialog
        wedding={wedding}
        open={true}
        onOpenChange={onOpenChange}
        onSuccess={onSuccess}
      />,
    );

    const convertBtn = screen.getByRole("button", {
      name: /efetivar casamento/i,
    });
    expect(convertBtn).not.toBeDisabled();

    const user = userEvent.setup();
    await user.click(convertBtn);

    await waitFor(() => {
      expect(toast.success).toHaveBeenCalledWith(
        "Casamento convertido para planejamento com sucesso!",
      );
      expect(onOpenChange).toHaveBeenCalledWith(false);
      expect(onSuccess).toHaveBeenCalled();
    });
  });
});
