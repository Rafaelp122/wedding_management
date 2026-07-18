import { describe, expect, it } from "vitest";
import { render, screen } from "@/test-utils";
import { UpcomingInstallmentsList } from "./UpcomingInstallmentsList";

describe("UpcomingInstallmentsList", () => {
  it("renders empty state when no installments are provided", () => {
    render(<UpcomingInstallmentsList installments={[]} />);
    expect(screen.getByText("Nenhum pagamento próximo.")).toBeInTheDocument();
  });

  it("renders list of upcoming installments", () => {
    const mockInstallments = [
      {
        uuid: "inst-1",
        installment_number: 1,
        amount: "1500.00",
        due_date: "2026-08-10",
        status: "PENDING",
      },
      {
        uuid: "inst-2",
        installment_number: 2,
        amount: "2000.00",
        due_date: "2026-07-20",
        status: "OVERDUE",
      },
    ];

    render(<UpcomingInstallmentsList installments={mockInstallments} />);

    expect(screen.getByText("Parcela #1")).toBeInTheDocument();
    expect(screen.getByText("Parcela #2")).toBeInTheDocument();
    expect(screen.getByText("Atrasado")).toBeInTheDocument();
    expect(screen.getByText("Pendente")).toBeInTheDocument();
  });
});
