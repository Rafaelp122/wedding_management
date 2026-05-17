import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@/test-utils";
import { createMockInstallment } from "@/test-data";
import { ExpenseInstallmentRow } from "@/features/finances/components/expenses/ExpenseInstallmentRow";
import type { InstallmentOut } from "@/api/generated/v1/models/installmentOut";
import { format } from "date-fns";
import { ptBR } from "date-fns/locale";


function renderRow(installment: InstallmentOut, isPaying = false) {
  const onTogglePayment = vi.fn();
  render(
    <table>
      <tbody>
        <ExpenseInstallmentRow
          installment={installment}
          isPaying={isPaying}
          onTogglePayment={onTogglePayment}
        />
      </tbody>
    </table>,
  );
  return { onTogglePayment };
}

describe("ExpenseInstallmentRow", () => {
  it("renders installment number correctly", () => {
    renderRow(createMockInstallment({ installment_number: 3 }));
    expect(screen.getByText("3")).toBeInTheDocument();
  });

  it("renders formatted amount with R$", () => {
    renderRow(createMockInstallment({ amount: "1500.50" }));
    expect(screen.getByText("R$ 1.500,50")).toBeInTheDocument();
  });

  it("renders formatted date (dd/MM/yyyy)", () => {
    const dueDate = "2026-06-15";
    renderRow(createMockInstallment({ due_date: dueDate }));
    const expectedDate = format(new Date(dueDate), "dd/MM/yyyy", {
      locale: ptBR,
    });
    expect(screen.getByText(expectedDate)).toBeInTheDocument();
  });

  describe("status badge", () => {
    it("shows PAID badge with Check icon and 'Pago' label", () => {
      renderRow(createMockInstallment({ status: "PAID" }));
      const badge = screen.getByText("Pago");
      expect(badge).toBeInTheDocument();
      // The Badge renders as a div — Check icon should be inside it
      const svg = badge.querySelector("svg");
      expect(svg).toBeInTheDocument();
    });

    it("shows PENDING badge with Clock icon and 'Pendente' label", () => {
      renderRow(createMockInstallment({ status: "PENDING" }));
      const badge = screen.getByText("Pendente");
      expect(badge).toBeInTheDocument();
      const svg = badge.querySelector("svg");
      expect(svg).toBeInTheDocument();
    });

    it("shows OVERDUE badge with AlertTriangle icon and 'Atrasado' label", () => {
      renderRow(createMockInstallment({ status: "OVERDUE" }));
      const badge = screen.getByText("Atrasado");
      expect(badge).toBeInTheDocument();
      const svg = badge.querySelector("svg");
      expect(svg).toBeInTheDocument();
    });
  });

  describe("toggle payment button", () => {
    it('shows "Desmarcar" button with destructive variant when status is PAID', () => {
      renderRow(createMockInstallment({ status: "PAID" }));
      const button = screen.getByRole("button", { name: /desmarcar/i });
      expect(button).toBeInTheDocument();
      // destructive variant adds a class with "destructive"
      expect(button.className).toContain("destructive");
    });

    it('shows "Marcar como Pago" button with outline variant when status is PENDING', () => {
      renderRow(createMockInstallment({ status: "PENDING" }));
      const button = screen.getByRole("button", { name: /marcar como pago/i });
      expect(button).toBeInTheDocument();
      // outline variant adds a class with "outline"
      expect(button.className).toContain("outline");
    });

    it("is disabled when isPaying is true", () => {
      renderRow(createMockInstallment({ status: "PENDING" }), true);
      const button = screen.getByRole("button", { name: /marcar como pago/i });
      expect(button).toBeDisabled();
    });

    it("is enabled when isPaying is false", () => {
      renderRow(createMockInstallment({ status: "PENDING" }), false);
      const button = screen.getByRole("button", { name: /marcar como pago/i });
      expect(button).toBeEnabled();
    });

    it('calls onTogglePayment with (uuid, false) when clicking "Marcar como Pago"', async () => {
      const { onTogglePayment } = renderRow(
        createMockInstallment({ uuid: "inst-test", status: "PENDING" }),
      );
      const { userEvent } = await import("@/test-utils");
      const button = screen.getByRole("button", { name: /marcar como pago/i });
      await userEvent.click(button);
      expect(onTogglePayment).toHaveBeenCalledWith("inst-test", false);
    });

    it('calls onTogglePayment with (uuid, true) when clicking "Desmarcar"', async () => {
      const { onTogglePayment } = renderRow(
        createMockInstallment({ uuid: "inst-test-2", status: "PAID" }),
      );
      const { userEvent } = await import("@/test-utils");
      const button = screen.getByRole("button", { name: /desmarcar/i });
      await userEvent.click(button);
      expect(onTogglePayment).toHaveBeenCalledWith("inst-test-2", true);
    });
  });
});
