import { describe, expect, it } from "vitest";
import { render, screen, waitFor } from "@/test-utils";
import { UpcomingInstallments } from "@/features/dashboard/components/UpcomingInstallments";
import { server } from "@/mocks/server";
import { createMockInstallment } from "@/test-data";

describe("UpcomingInstallments", () => {
  it("does not crash on render", () => {
    expect(() => render(<UpcomingInstallments />)).not.toThrow();
  });

  it("shows pending installments when data exists", async () => {
    const { http, HttpResponse } = await import("msw");
    const today = new Date();
    const in3days = new Date(today);
    in3days.setDate(in3days.getDate() + 3);
    const dueDate = in3days.toISOString().slice(0, 10);

    server.use(
      http.get("*/api/v1/finances/installments/", () =>
        HttpResponse.json(
          {
            items: [
              createMockInstallment({
                uuid: "inst-1",
                installment_number: 1,
                amount: "500.00",
                due_date: dueDate,
                status: "PENDING",
              }),
            ],
            count: 1,
          },
        ),
      ),
    );

    render(<UpcomingInstallments />);

    await waitFor(() => {
      expect(screen.getByText("Parcelas a Vencer")).toBeInTheDocument();
      expect(screen.getByText(/Parcela #1/)).toBeInTheDocument();
      expect(screen.getByText("7d")).toBeInTheDocument();
      expect(screen.getByText("14d")).toBeInTheDocument();
      expect(screen.getByText("30d")).toBeInTheDocument();
    });
  });
});
