import { describe, expect, it, vi } from "vitest";
import { render, screen, userEvent, waitFor } from "@/test-utils";
import { PlannerContractDialog } from "./PlannerContractDialog";
import { toast } from "sonner";
import { createMockPlannerContract } from "@/test-data";

describe("PlannerContractDialog", () => {
  it("renders nothing when closed", () => {
    render(
      <PlannerContractDialog
        weddingUuid="w-1"
        open={false}
        onOpenChange={vi.fn()}
      />,
    );

    expect(
      screen.queryByText("Contrato de Assessoria"),
    ).not.toBeInTheDocument();
  });

  it("renders form fields correctly when open", () => {
    render(
      <PlannerContractDialog
        weddingUuid="w-1"
        open={true}
        onOpenChange={vi.fn()}
      />,
    );

    expect(screen.getByText("Contrato de Assessoria")).toBeInTheDocument();
    expect(screen.getByLabelText("Nível de Serviço")).toBeInTheDocument();
    expect(
      screen.getByLabelText("Valor dos Honorários (R$)"),
    ).toBeInTheDocument();
    expect(screen.getByLabelText("Número de Parcelas")).toBeInTheDocument();
    expect(screen.getByLabelText("Data de Assinatura")).toBeInTheDocument();
    expect(screen.getByLabelText("Status do Contrato")).toBeInTheDocument();
  });

  it("submits valid form data and triggers success feedback", async () => {
    const onSuccess = vi.fn();
    const onOpenChange = vi.fn();

    render(
      <PlannerContractDialog
        weddingUuid="w-1"
        open={true}
        onOpenChange={onOpenChange}
        onSuccess={onSuccess}
      />,
    );

    const user = userEvent.setup();
    const feeInput = screen.getByLabelText("Valor dos Honorários (R$)");
    await user.clear(feeInput);
    await user.type(feeInput, "6000");

    const installmentsInput = screen.getByLabelText("Número de Parcelas");
    await user.clear(installmentsInput);
    await user.type(installmentsInput, "3");

    const submitBtn = screen.getByRole("button", {
      name: /salvar contrato/i,
    });
    await user.click(submitBtn);

    await waitFor(() => {
      expect(toast.success).toHaveBeenCalledWith(
        "Contrato de assessoria salvo com sucesso!",
      );
      expect(onOpenChange).toHaveBeenCalledWith(false);
      expect(onSuccess).toHaveBeenCalled();
    });
  });

  it("loads existing contract data when editing", () => {
    const existingContract = createMockPlannerContract({
      service_tier: "PARCIAL",
      effective_amount: "4500.00",
      installments_count: 4,
      signed_date: "2025-05-20",
      status: "SIGNED",
    });

    render(
      <PlannerContractDialog
        weddingUuid="w-1"
        contract={existingContract}
        open={true}
        onOpenChange={vi.fn()}
      />,
    );

    expect(
      screen.getByText("Editar Contrato de Assessoria"),
    ).toBeInTheDocument();
    expect(screen.getByLabelText("Valor dos Honorários (R$)")).toHaveValue(
      4500,
    );
    expect(screen.getByLabelText("Número de Parcelas")).toHaveValue(4);
    expect(screen.getByLabelText("Data de Assinatura")).toHaveValue(
      "2025-05-20",
    );
  });
});
