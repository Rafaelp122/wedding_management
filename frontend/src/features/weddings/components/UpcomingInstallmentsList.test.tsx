import { describe, expect, it } from "vitest";
import { faker } from "@faker-js/faker";
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
        uuid: faker.string.uuid(),
        installment_number: 1,
        amount: faker.finance.amount({ min: 1000, max: 2000, dec: 2 }),
        due_date: faker.date.future().toISOString().split("T")[0],
        status: "PENDING",
      },
      {
        uuid: faker.string.uuid(),
        installment_number: 2,
        amount: faker.finance.amount({ min: 2001, max: 3000, dec: 2 }),
        due_date: faker.date.past().toISOString().split("T")[0],
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
